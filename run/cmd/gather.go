package cmd

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/makkes/judo/process"
	"github.com/spf13/cobra"
)

var gatherCommand = &cobra.Command{
	Use:   "gather",
	Short: "start data gathering process from meter",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		baseVal := args[0]
		
		p, err := exec.LookPath("python3")
		if err != nil {
			return fmt.Errorf("could not lookup python3 path: %w", err)
		}
		out, err := os.OpenFile("../01-plot/meter.csv", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0640)
		if err != nil {
			return fmt.Errorf("could not open log file: %w", err)
		}
		_, sigCh := process.Start(p, []string{"capture.py", baseVal}, "../00-capture", out)
		res := <-sigCh
		if res.Err != nil {
			return fmt.Errorf("error gathering values: %w", res.Err)
		}
		if res.ExitCode != 0 {
			return fmt.Errorf("error gathering values: exit status %d", res.ExitCode)
		}

		return nil
	},
}
