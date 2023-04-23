while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
done

while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
      sleep 0.1
done