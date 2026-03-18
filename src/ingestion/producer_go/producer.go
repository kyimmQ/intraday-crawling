package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/joho/godotenv"
	"github.com/kyimmQ/go-fcdata/client"
	"github.com/kyimmQ/go-fcdata/models"
	"github.com/kyimmQ/go-fcdata/signalr"
	"github.com/redis/go-redis/v9"
)

var (
	redisURL  = getEnv("REDIS_URL", "redis://localhost:6379")
	streamKey = "market:ticks"
	stocks    = []string{"41I1G3000", "41I1G4000"}
)

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok && value != "" {
		return value
	}
	return fallback
}

func main() {
	// Read consumer credentials from environment variables
	_ = godotenv.Load() // Load .env file if it exists, but ignore errors
	consumerID := getEnv("CONSUMER_ID", "")
	consumerSecret := getEnv("CONSUMER_SECRET", "")
	if consumerID == "" || consumerSecret == "" {
		log.Fatalf("CONSUMER_ID and CONSUMER_SECRET must be set")
	}

	// Setup context that listens to SIGINT and SIGTERM
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigs
		log.Println("Received termination signal")
		cancel()
	}()

	// Connect to Redis
	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Invalid REDIS_URL: %v", err)
	}
	rdb := redis.NewClient(opts)
	defer rdb.Close()

	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}

	// Authenticate via REST API to get the token
	log.Println("Authenticating to FCData...")
	fcClient := client.NewFCDataClient("")
	tokenResponse, err := fcClient.Login(consumerID, consumerSecret)
	if err != nil {
		log.Fatalf("Login failed: %v", err)
	}
	log.Println("Login successful!")

	// Channel for pushing JSON strings to Redis
	msgChan := make(chan string, 10000)

	// Start Redis worker
	go redisWorker(ctx, rdb, msgChan)

	// Connect to SignalR using the obtained token
	streamClient := signalr.NewClient("https://fc-datahub.ssi.com.vn/v2.0/signalr", tokenResponse)

	streamClient.OnConnected = func() {
		log.Println("SignalR Connected!")
		for _, stock := range stocks {
			channel := "X-TRADE:" + stock
			streamClient.SwitchChannel(channel)
			log.Printf("Subscribed to %s", channel)
		}
	}

	streamClient.OnData = func(msg models.BroadcastMessage) {
		// Only process XTradeData
		if tradeData, ok := msg.Data.(models.XTradeData); ok {
			jsonBytes, err := json.Marshal(tradeData)
			if err != nil {
				log.Printf("Error marshaling XTradeData: %v", err)
				return
			}

			// Non-blocking send to prevent stalling the SignalR loop
			select {
			case <-ctx.Done():
				return
			case msgChan <- string(jsonBytes):
				// Successfully enqueued
			default:
				// Channel is full; drop the message to avoid blocking SignalR receive loop.
				log.Printf("Dropping message due to full msgChan buffer")
			}
		}
	}

	streamClient.OnError = func(err error) {
		log.Printf("SignalR Error: %v", err)
	}

	// Run SignalR client loop
	go func() {
		streamClient.StartWithLoop()
	}()

	// Wait for context cancellation
	<-ctx.Done()
	log.Println("Exiting application...")
}

func redisWorker(ctx context.Context, rdb *redis.Client, msgChan <-chan string) {
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-msgChan:
			err := rdb.XAdd(ctx, &redis.XAddArgs{
				Stream: streamKey,
				Values: map[string]interface{}{
					"data": msg,
				},
			}).Err()

			if err != nil {
				log.Printf("Error pushing to Redis: %v", err)
			}
		}
	}
}
