package main

import (
	"context"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/websocket"
	"github.com/redis/go-redis/v9"
)

var (
	redisURL  = getEnv("REDIS_URL", "redis://localhost:6379")
	streamKey = "market:ticks_legacy"
	wsURL     = "wss://iboard-pushstream.ssi.com.vn/realtime"
	stocks    = []string{"41I1G3000", "41I1G4000"}
)

func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

func main() {
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

	// Parse Redis URL and connect
	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Invalid REDIS_URL: %v", err)
	}
	rdb := redis.NewClient(opts)
	defer rdb.Close()

	// Ensure Redis is reachable
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("Could not connect to Redis: %v", err)
	}

	// Create a buffered channel for decoupling read and publish
	// A large buffer helps handle bursty market data
	msgChan := make(chan []byte, 10000)

	// Start Redis publisher worker
	go redisWorker(ctx, rdb, msgChan)

	// Main retry loop for WebSocket connection
	for {
		select {
		case <-ctx.Done():
			log.Println("Exiting application...")
			return
		default:
			log.Printf("Connecting to %s...", wsURL)
			err := connectAndRead(ctx, msgChan)
			if err != nil {
				log.Printf("WebSocket error: %v", err)
			}
			log.Println("Reconnecting in 5 seconds...")
			time.Sleep(5 * time.Second)
		}
	}
}

// connectAndRead establishes connection and reads messages in a blocking way
func connectAndRead(ctx context.Context, msgChan chan<- []byte) error {
	dialer := websocket.Dialer{
		HandshakeTimeout: 10 * time.Second,
	}

	conn, _, err := dialer.DialContext(ctx, wsURL, nil)
	if err != nil {
		return err
	}
	defer conn.Close()

	log.Println("Connected!")

	// Send subscription message
	subscribeMsg := map[string]interface{}{
		"type":      "sub",
		"topic":     "stockRealtimeByListV2",
		"component": "priceTableEquities",
		"variables": stocks,
	}

	msgBytes, err := json.Marshal(subscribeMsg)
	if err != nil {
		return err
	}

	err = conn.WriteMessage(websocket.TextMessage, msgBytes)
	if err != nil {
		return err
	}
	log.Printf("Subscribed to %v", stocks)

	// Keep-alive routine
	// The Python code had ping_interval=60
	go func() {
		ticker := time.NewTicker(60 * time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				if err := conn.WriteControl(websocket.PingMessage, []byte{}, time.Now().Add(5*time.Second)); err != nil {
					log.Printf("Ping error: %v", err)
					return
				}
			}
		}
	}()

	// Read messages
	for {
		select {
		case <-ctx.Done():
			return nil
		default:
			_, message, err := conn.ReadMessage()
			if err != nil {
				return err
			}
			// Push raw message to channel
			msgChan <- message
		}
	}
}

// redisWorker reads from the channel and pushes to Redis
func redisWorker(ctx context.Context, rdb *redis.Client, msgChan <-chan []byte) {
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-msgChan:
			err := rdb.XAdd(ctx, &redis.XAddArgs{
				Stream: streamKey,
				Values: map[string]interface{}{
					"raw": string(msg),
				},
			}).Err()

			if err != nil {
				log.Printf("Error pushing to Redis: %v", err)
			}
		}
	}
}
