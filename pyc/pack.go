package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

var srcpath = "/Users/zhengjunling/go/src/github.com/youtube/yt-dlp/yt_dlp/"
var pypath = "/Users/zhengjunling/go/src/github.com/youtube/yt-dlp/pyc/"
var destpath = "/Users/zhengjunling/go/src/github.com/youtube/yt-dlp/pyc/yt_dlp/"
var PycSymbol = "-37.opt-1.pyc"
var Cpy = ".cpython"
var Pyc = "__pycache__"

func main() {
	fmt.Println("main start...")
	err := CopyDir(srcpath, destpath)
	if err != nil {
		fmt.Println("err:", err)
		return
	}
	_, err = copyFile(srcpath+"__main__.py", pypath+"__main__.py")
	if err != nil {
		fmt.Println("err:", err)
		return
	}
}

func CopyDir(srcPath string, destPath string) error {
	if srcInfo, err := os.Stat(srcPath); err != nil {
		fmt.Println(err.Error())
		return err
	} else {
		if !srcInfo.IsDir() {
			e := errors.New("srcPath不是一个正确的目录！")
			fmt.Println(e.Error())
			return e
		}
	}
	if destInfo, err := os.Stat(destPath); err != nil {
		fmt.Println(err.Error())
		return err
	} else {
		if !destInfo.IsDir() {
			e := errors.New("destInfo不是一个正确的目录！")
			fmt.Println(e.Error())
			return e
		}
	}
	//加上拷贝时间:不用可以去掉
	// destPath = destPath + "_" + time.Now().Format("20060102150405")

	err := filepath.Walk(srcPath, func(path string, f os.FileInfo, err error) error {
		if f == nil {
			return err
		}
		if !f.IsDir() {
			if strings.HasSuffix(f.Name(), PycSymbol) || f.Name() == "__main__.py" {
				path := strings.Replace(path, "\\", "/", -1)
				destNewPath := strings.Replace(path, srcPath, destPath, -1)
				if strings.HasSuffix(f.Name(), PycSymbol) {
					destNewPath = strings.Replace(destNewPath, PycSymbol, ".pyc", -1)
					destNewPath = strings.Replace(destNewPath, Cpy, "", -1)
					destNewPath = strings.Replace(destNewPath, Pyc, "", -1)
				}
				fmt.Println("复制文件:" + path + " 到 " + destNewPath)
				copyFile(path, destNewPath)
			}
		}
		return nil
	})
	if err != nil {
		fmt.Printf(err.Error())
	}
	return err
}

//生成目录并拷贝文件
func copyFile(src, dest string) (w int64, err error) {
	//分割path目录
	destSplitPathDirs := strings.Split(dest, "/")

	//检测时候存在目录
	destSplitPath := ""
	for index, dir := range destSplitPathDirs {
		if index < len(destSplitPathDirs)-1 {
			destSplitPath = destSplitPath + dir + "/"
			b, _ := pathExists(destSplitPath)
			if b == false {
				// fmt.Println("创建目录:" + destSplitPath)
				//创建目录
				err := os.Mkdir(destSplitPath, os.ModePerm)
				if err != nil {
					fmt.Println(err)
				}
			}
		}
	}

	srcFile, err := os.Open(src)
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	defer srcFile.Close()
	dstFile, err := os.Create(dest)
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	defer dstFile.Close()

	return io.Copy(dstFile, srcFile)
}

func pathExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}
