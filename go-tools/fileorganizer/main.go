package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

var (
	src     = flag.String("src", ".", "Source directory")
	dest    = flag.String("dest", ".", "Destination directory")
	mode    = flag.String("mode", "dry", "Mode: move|copy|dry")
	flatten = flag.Bool("flatten", false, "Ignore subdirs in destination names")
)

var typeMap = map[string]string{
	".jpg":"Images",".jpeg":"Images",".png":"Images",".gif":"Images",".webp":"Images",
	".mp4":"Videos",".mov":"Videos",".mkv":"Videos",
	".mp3":"Audio",".wav":"Audio",".flac":"Audio",
	".pdf":"Docs",".doc":"Docs",".docx":"Docs",".xls":"Docs",".xlsx":"Docs",".ppt":"Docs",".pptx":"Docs",".txt":"Docs",".md":"Docs",
	".zip":"Archives",".tar":"Archives",".gz":"Archives",".7z":"Archives",
	".go":"Code",".py":"Code",".js":"Code",".ts":"Code",".java":"Code",".cs":"Code",".rb":"Code",".php":"Code",
}

func classify(name string) string {
	ext := strings.ToLower(filepath.Ext(name))
	if t, ok := typeMap[ext]; ok { return t }
	return "Other"
}

func ensureDir(path string) error { return os.MkdirAll(path, 0o755) }

func copyFile(src, dst string) error {
	in, err := os.Open(src); if err != nil { return err }
	defer in.Close()
	if err := ensureDir(filepath.Dir(dst)); err != nil { return err }
	out, err := os.Create(dst); if err != nil { return err }
	defer func(){ _=out.Close() }()
	if _, err := io.Copy(out, in); err != nil { return err }
	return out.Sync()
}

func moveFile(src, dst string) error {
	if err := ensureDir(filepath.Dir(dst)); err != nil { return err }
	return os.Rename(src, dst)
}

func main() {
	flag.Parse()
	if _, err := os.Stat(*src); err != nil {
		fmt.Fprintf(os.Stderr, "Source error: %v\n", err); os.Exit(2)
	}
	if err := ensureDir(*dest); err != nil {
		fmt.Fprintf(os.Stderr, "Dest error: %v\n", err); os.Exit(2)
	}

	err := filepath.WalkDir(*src, func(p string, d os.DirEntry, err error) error {
		if err != nil { return err }
		if d.IsDir() { return nil }
		rel, _ := filepath.Rel(*src, p)
		targetDir := classify(d.Name())
		if !*flatten {
			if dir := filepath.Dir(rel); dir != "." { targetDir = filepath.Join(targetDir, dir) }
		}
		dst := filepath.Join(*dest, targetDir, d.Name())

		switch *mode {
		case "copy":
			fmt.Printf("[COPY] %s -> %s\n", p, dst)
			return copyFile(p, dst)
		case "move":
			fmt.Printf("[MOVE] %s -> %s\n", p, dst)
			return moveFile(p, dst)
		default:
			fmt.Printf("[DRY]  %s -> %s\n", p, dst)
			return nil
		}
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err); os.Exit(1)
	}
}
