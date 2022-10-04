package cmd

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"sync"
	"time"

	"github.com/makkes/judo/process"
	"github.com/spf13/cobra"
)

func plot(dir string, days int) {
	_, sigCh := process.Start("./plot.sh", []string{strconv.Itoa(days)}, dir, os.Stdout)
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

func dispatchPlotters(out io.Writer, days int, basedir string) error {
	ticker := time.Tick(10 * time.Minute)
	var wg sync.WaitGroup
	for {
		fmt.Fprintf(out, "[%s] plotting graphs\n", time.Now().Format(time.RFC3339))
		if err := filepath.Walk(filepath.Join(basedir, "01-plot"), func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return fmt.Errorf("error walking plot dir: %w", err)
			}
			if info.IsDir() {
				wg.Add(1)
				go func() {
					defer wg.Done()
					plot(path, days)
				}()
				wg.Wait()
			}
			return nil
		}); err != nil {
			return fmt.Errorf("error walking dir: %w", err)
		}
		fmt.Fprintf(out, "[%s] plotting done\n", time.Now().Format(time.RFC3339))
		<-ticker
	}
}

func NewPlotCommand(basedirFlag *string) *cobra.Command {
	var days int
	cmd := &cobra.Command{
		Use:   "plot",
		Short: "plot all graphs from gathered data",
		RunE: func(cmd *cobra.Command, args []string) error {
			return dispatchPlotters(cmd.OutOrStdout(), days, *basedirFlag)
		},
	}

	cmd.Flags().IntVar(&days, "days", 30, "number of days to plot")

	return cmd
}
