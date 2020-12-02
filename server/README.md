# pre-conditions
ssh key to access github
aws credential
env.yml (see ../env/README)

# build docker image
```
$ cp ../env/env.yml .
$ DOCKER_BUILDKIT=1 docker build -t tile-score-server --ssh default .
```

# run docker image
```
$ docker run -it --rm -v ~/.ssh:/root/.ssh -v ~/.aws:/root/.aws tile-score-server /bin/bash
```

# deploy to dev
```
# npx sls deploy
```

# deploy to prod
```
# npx sls deploy --stage prod
```

# test
```bash
# bash test.sh <endpoint>
```
