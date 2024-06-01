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
	"net/http"
	"time"
)

type Template struct {
	templates *template.Template
}

func (t *Template) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

type Data struct {
	Timestamp time.Time
	Topic     string
}

type PageData struct {
	DataList       []Data
	IsQueryRunning bool
}

const uri = "mongodb://localhost:27017"

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
	fmt.Println("Pinged your deployment. You successfully connected to MongoDB!")

    //read collection proxy

    collection := client.Database("QueryMan").Collection("proxy")
    ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
    cursor, err := collection.Find(ctx, bson.M{})
    if err != nil {
        panic(err)
    }
    defer cursor.Close(ctx)
    for cursor.Next(ctx) {
        var result bson.M
        err := cursor.Decode(&result)
        if err != nil {
            panic(err)
        }
        fmt.Println(result["ip"])
    }


	e := echo.New()
	e.Use(middleware.Logger())

	e.Static("/", "public")

	pageData := PageData{
		DataList:       []Data{},
		IsQueryRunning: false,
	}

	t := &Template{
		templates: template.Must(template.ParseGlob("views/*.html")),
	}

	e.Renderer = t

	e.GET("/", func(c echo.Context) error {
		fmt.Println("pageData.IsQueryRunning: ", pageData.IsQueryRunning)
		return c.Render(http.StatusOK, "index", pageData)
	})

	e.POST("/query", func(c echo.Context) error {
		fmt.Println("querying X")
		if !pageData.IsQueryRunning {
			pageData.IsQueryRunning = true
		}
	       err := c.Render(http.StatusOK, "form", pageData.IsQueryRunning)
		if err != nil {
			return err
		}
	       return nil;
	})

	e.Logger.Fatal(e.Start(":42069"))
}
