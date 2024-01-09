<h1 align="center">Sentiment Analysis Backend</h1>


## Setup

Switch to dwoc24 branch

1. Configurations

```
cp app/config.example.py app/config.py
```

2. ML Model

```
git submodule update --init
```
3. Run the Application

Linux/MacOs
```
python3 run.py
```
Windows
```
python run.py
```


## ML Model

If you want to make changes to the ML Model (and want your changes to be reflected in the backend), follow these steps

1. Fork and Clone the remote ML repository
Link:
```
https://github.com/codx-aks/sentimentAnalysis
```
2. Switch to dwoc24 and delete the .gitmodules file
```
rm -rf .gitmodules
```

3. Add your repo as a submodule
```
git add submodule <your_cloned_ml_repo>
```
Start making your changes

If you don't want your changes to be reflected in the backend, just work in the ML repo seperately and give pull requests to it directly