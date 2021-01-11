package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/makkes/judo/process"
)

func plot(dir string) {
	_, sigCh := process.Start("./plot.sh", nil, dir, os.Stdout)
	res := <-sigCh
	if res.Err != nil {
		fmt.Fprintf(os.Stderr, "error plotting graph in %s: %s\n", dir, res.Err)
	}
	if res.ExitCode != 0 {
		fmt.Fprintf(os.Stderr, "error plotting graph in %s: exit status %d\n", dir, res.ExitCode)
	}
}

func gatherValues(baseVal string) {
	p, err := exec.LookPath("python3")
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not lookup python3 path: %s\n", err)
		os.Exit(1)
	}
	out, err := os.OpenFile("../01-plot/meter.csv", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0640)
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not open log file: %s\n", err)
		os.Exit(1)
	}
	_, sigCh := process.Start(p, []string{"capture.py", baseVal}, "../00-capture", out)
	res := <-sigCh
	if res.Err != nil {
		fmt.Fprintf(os.Stderr, "error gathering values: %s\n", res.Err)
	}
	if res.ExitCode != 0 {
		fmt.Fprintf(os.Stderr, "error gathering values: exit status %d\n", res.ExitCode)
	}
}

func dispatchPlotters() {
	ticker := time.Tick(60 * time.Second)
	for {
		if err := filepath.Walk("../01-plot", func(path string, info os.FileInfo, err error) error {
			if info.IsDir() {
				go plot(path)
			}
			return nil
		}); err != nil {
			fmt.Fprintf(os.Stderr, "error walking dir: %s", err)
		}
		<-ticker
	}
}

func main() {
	quitCh := make(chan struct{})

	switch os.Args[1] {
	case "plot":
		go dispatchPlotters()
	case "gather":
		go gatherValues(os.Args[2])
	}

	<-quitCh
}
