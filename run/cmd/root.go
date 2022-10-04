package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

func Execute() {
	rootCmd := &cobra.Command{
		Use:          "smartmeter",
		SilenceUsage: true,
	}

	var baseDirFlag string

	rootCmd.AddCommand(NewGatherCommand(&baseDirFlag))
	rootCmd.AddCommand(NewPlotCommand(&baseDirFlag))

	wd, err := os.Getwd()
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not get current working directory: %s", err)
		os.Exit(1)
	}
	rootCmd.PersistentFlags().StringVar(&baseDirFlag, "base-dir", wd, "base directory in which to search for scripts")

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
