package main

import (
	"context"
	"fmt"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"time"
)

var mutex sync.Mutex
var isRunning bool = false

const uri = "mongodb://localhost:27017"
const readableTimeFormat = "02 Jan 2006 15:04:05"
const logTimeFormat = "02012006150405"

type proxy struct {
	Ip   string `bson:"ip"`
	Port int    `bson:"port"`
}

type Logs struct {
	Timestamp time.Time `bson:"timestamp"`
	LogFile   string    `bson:"logfile"`
	ExitCode  int       `bson:"exitCode"`
}

type LogsReadable struct {
	Timestamp string `bson:"timestamp"`
	LogFile   string `bson:"logfile"`
	ExitCode  int    `bson:"exitCode"`
}

type Template struct {
	templates *template.Template
}

func (t *Template) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

type Trending struct {
	Ip     string `bson:"ip"`
	Date   string `bson:"date"`
	Topics bson.D `bson:"topics" json:"topics"`
}

type Data struct {
	Ip     string            `bson:"ip"`
	Date   string            `bson:"date"`
	Topics map[string]string `bson:"topics" json:"topics"`
}

type PageData struct {
	DataList  []Data
	Logs      []LogsReadable
	IsRunning bool
}

func insertLog(client *mongo.Client, log_file string, timestamp time.Time, exitCode int) error {
	var log1 Logs
	log1.Timestamp = timestamp
	log1.ExitCode = exitCode
	log1.LogFile = log_file

	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	_, err := client.Database("QueryMan").Collection("logs").InsertOne(ctx, log1)

	if err != nil {
		log.Fatal(err)
		return err
	}
	return nil
}

func runBashScript(client *mongo.Client) error {
	curdir, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
		return err
	}
	today := time.Now()
	todayStr := string(today.Format(logTimeFormat))
	log_file := curdir + "/logs/Run_" + todayStr + ".log"

	script := curdir + "/scripts/selenium/runner.sh"

	args := []string{
		"us-ca.proxymesh.com",
		"31280",
		log_file,
	}

	exitCode := 0
	cmd := exec.Command(script, args...)
	fmt.Println("Running command: ", cmd.String())
	out, err := cmd.Output()
	if err != nil {
		fmt.Println(err)
		exitCode = 1
	}
	fmt.Println("stdout: ", string(out))

	err = insertLog(client, log_file, today, exitCode)
	if err != nil {
		log.Fatal(err)
	}
	return nil
}

func getLogs(client *mongo.Client) []LogsReadable {
	collection := client.Database("QueryMan").Collection("logs")
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		panic(err)

	}
	defer cursor.Close(ctx)

	var logs []Logs
	if err = cursor.All(ctx, &logs); err != nil {
		panic(err)
	}

	//convert to readable logs
	var readableLogs []LogsReadable
	for _, log := range logs {
		var logReadable LogsReadable
		logReadable.Timestamp = string(log.Timestamp.Format(readableTimeFormat))
		logReadable.LogFile = log.LogFile
		logReadable.ExitCode = log.ExitCode
		readableLogs = append(readableLogs, logReadable)
	}
	return readableLogs
}

func getTrendingData(client *mongo.Client) []Data {
	collection := client.Database("QueryMan").Collection("trending")
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		panic(err)
	}
	defer cursor.Close(ctx)

	var topics []Trending
	var data []Data
	if err = cursor.All(ctx, &topics); err != nil {
		panic(err)
	}

	for _, topic := range topics {
		var d Data
		d.Ip = topic.Ip
		tmp, err := time.Parse(logTimeFormat, topic.Date)
		if err != nil {
			panic(err)
		}
		d.Date = string(tmp.Format(readableTimeFormat))

		topicList := make(map[string]string)
		for _, t := range topic.Topics {
			topicList[t.Key] = fmt.Sprintf("%v", t.Value)
		}
		d.Topics = topicList

		data = append(data, d)
	}
	return data
}

func main() {
	serverAPI := options.ServerAPI(options.ServerAPIVersion1)
	opts := options.Client().ApplyURI(uri).SetServerAPIOptions(serverAPI)
	client, err := mongo.Connect(context.TODO(), opts)
	if err != nil {
		panic(err)
	}
	defer func() {
		if err = client.Disconnect(context.TODO()); err != nil {
			panic(err)
		}
	}()
	var result bson.M
	if err := client.Database("QueryMan").RunCommand(context.TODO(), bson.D{{"ping", 1}}).Decode(&result); err != nil {
		panic(err)
	}
	fmt.Println("Successfully connected to MongoDB!")

	e := echo.New()
	e.Use(middleware.Logger())

	e.Static("/", "public")

	pageData := PageData{
		DataList:  []Data{},
		Logs:      []LogsReadable{},
		IsRunning: false,
	}

	t := &Template{
		templates: template.Must(template.ParseGlob("views/*.html")),
	}

	e.Renderer = t

	e.GET("/", func(c echo.Context) error {
		logs := getLogs(client)
		topics := getTrendingData(client)

        fmt.Println("len of topics: ", len(topics))

		pageData.DataList = topics
		pageData.Logs = logs

		return c.Render(http.StatusOK, "index", pageData)
	})

	e.POST("/query", func(c echo.Context) error {
		if isRunning {
			return c.Render(http.StatusOK, "form", pageData.IsRunning)
		} else {
			isRunning = true
			go func() {
				runBashScript(client)
			}()
			isRunning = false
		}
		err := c.Render(http.StatusOK, "form", pageData.IsRunning)
		if err != nil {
			return err
		}
		return nil
	})

	e.GET("/data", func(c echo.Context) error {
		topics := getTrendingData(client)
		pageData.DataList = topics
		return c.Render(http.StatusOK, "data", pageData.DataList)
	})

	e.GET("/logs", func(c echo.Context) error {
		pageData.Logs = getLogs(client)
		err = c.Render(http.StatusOK, "logs", pageData.Logs)
		if err != nil {
			return err
		}
		return nil
	})

	e.Logger.Fatal(e.Start(":42069"))
}
