package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/makkes/judo/process"
	"github.com/spf13/cobra"
)

func NewGatherCommand(basedirFlag *string) *cobra.Command {
	var dummyFlag bool
	cmd := &cobra.Command{
		Use:   "gather BASE_VALUE",
		Short: "start data gathering process from meter, starting with BASE_VAL as start meter value",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			baseVal := args[0]

			p, err := exec.LookPath("python3")
			if err != nil {
				return fmt.Errorf("could not lookup python3 path: %w", err)
			}
			out, err := os.OpenFile(filepath.Join(*basedirFlag, "01-plot", "meter.csv"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0640)
			if err != nil {
				return fmt.Errorf("could not open log file: %w", err)
			}
			argv := []string{"capture.py", baseVal}
			if dummyFlag {
				argv = append(argv, "DUMMY")
			}
			_, sigCh := process.Start(p, argv, filepath.Join(*basedirFlag, "00-capture"), out)
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

	cmd.Flags().BoolVar(&dummyFlag, "dummy", false, "generate dummy values. Useful for testing without access to an actual meter.")

	return cmd
}
