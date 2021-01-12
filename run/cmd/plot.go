package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/makkes/judo/process"
	"github.com/spf13/cobra"
)

func plot(dir string) {
	_, sigCh := process.Start("./plot.sh", nil, dir, os.Stdout)
	res := <-sigCh
	if res.Err != nil {
		fmt.Fprintf(os.Stderr, "error plotting graph in %s: %s\n", dir, res.Err)
		return
	}
	if res.ExitCode != 0 {
		fmt.Fprintf(os.Stderr, "error plotting graph in %s: exit status %d\n", dir, res.ExitCode)
		return
	}
}

func dispatchPlotters() error {
	ticker := time.Tick(60 * time.Second)
	var wg sync.WaitGroup
	for {
		if err := filepath.Walk("../01-plot", func(path string, info os.FileInfo, err error) error {
			if info.IsDir() {
				wg.Add(1)
				go func() {
					defer wg.Done()
					plot(path)
				}()
				wg.Wait()
			}
			return nil
		}); err != nil {
			return fmt.Errorf("error walking dir: %w", err)
		}
		<-ticker
	}
}

var plotCommand = &cobra.Command{
	Use:   "plot",
	Short: "plot all graphs from gathered data",
	RunE: func(cmd *cobra.Command, args []string) error {
		dispatchPlotters()
		return nil
	},
}
