## To run :monkey: :

1. docker pull elasticsearch:5.2.2-alpine
2. docker build -t enisa:moloch . 
3. docker run -d --name es elasticsearch:5.2.2-alpine
4. docker run --name moloch -p 8005:8005 -d --link es:elasticsearch enisa:moloch

