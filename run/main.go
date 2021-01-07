package main

import (
	"fmt"
	"os"
	"time"

	"github.com/makkes/judo/process"
)

func plotValues() {
	ticker := time.Tick(60 * time.Second)
	for {
		_, sigCh := process.Start("/usr/bin/gnuplot", []string{"plot.gnuplot"}, "../01-plot")
		res := <-sigCh
		if res.Err != nil {
			fmt.Fprintf(os.Stderr, "error running gnuplot: %s\n", res.Err)
		}
		if res.ExitCode != 0 {
			fmt.Fprintf(os.Stderr, "error running gnuplot: exit status %d\n", res.ExitCode)
		}
		<-ticker
	}
}

func plotDaily() {
	ticker := time.Tick(1 * time.Hour)
	for {
		_, sigCh := process.Start("./plot.sh", nil, "../01-plot/daily")
		res := <-sigCh
		if res.Err != nil {
			fmt.Fprintf(os.Stderr, "error plotting daily graph: %s\n", res.Err)
		}
		if res.ExitCode != 0 {
			fmt.Fprintf(os.Stderr, "error plotting daily graph: exit status %d\n", res.ExitCode)
		}
		<-ticker
	}
}

func gatherValues(baseVal string) {
	_, sigCh := process.Start("./capture.sh", []string{baseVal}, "../00-capture")
	res := <-sigCh
	if res.Err != nil {
		fmt.Fprintf(os.Stderr, "error gathering values: %s\n", res.Err)
	}
	if res.ExitCode != 0 {
		fmt.Fprintf(os.Stderr, "error gathering values: exit status %d\n", res.ExitCode)
	}
}

func main() {
	quitCh := make(chan struct{})

	go plotValues()
	go plotDaily()
	go gatherValues(os.Args[1])

	<-quitCh
}
