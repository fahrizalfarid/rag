/*
Copyright © 2025 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"time"

	v1 "github.com/fahrizalfarid/rag/src/delivery/router/api/v1"
	"github.com/fahrizalfarid/rag/src/usecase"
	"github.com/gofiber/fiber/v2"
	"github.com/spf13/cobra"
)

// serverCmd represents the server command
var serverCmd = &cobra.Command{
	Use:   "server",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("server called")

		app := fiber.New()
		ragUsecase := usecase.NewRAGUsecase()
		v1.NewRagDelivery(app, ragUsecase)
		go func() {
			app.Listen(":8082")
		}()

		m := make(chan os.Signal, 1)
		signal.Notify(m, os.Interrupt, os.Kill)
		<-m
		log.Println("graceful shutdown...")
		time.Sleep(2 * time.Second)
		app.Shutdown()
		os.Exit(1)
	},
}

func init() {
	rootCmd.AddCommand(serverCmd)

	// environment here & config
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// serverCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// serverCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
