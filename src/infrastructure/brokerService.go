package infrastructure

import "github.com/nats-io/nats.go"

func NatsConn() (*nats.Conn, error) {
	nc, err := nats.Connect(nats.DefaultURL)
	if err != nil {
		return nil, err
	}
	return nc, nil
}
