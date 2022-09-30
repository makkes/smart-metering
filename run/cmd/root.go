package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:          "smartmeter",
	SilenceUsage: true,
}

func Execute() {
	rootCmd.AddCommand(NewGatherCommand())
	rootCmd.AddCommand(plotCommand)

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
