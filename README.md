# Neural A&R: Hit Song Predictor

This repo contains the code written during our final research project for UMass’s CS-682: Neural Networks course! The culmination of this research project is our paper, Improving Hit Song Prediction with Music Industry Co-Collaboration Network Data. 

In the paper, we improve upon previous solutions to the “Hit Song Science” problem; this problem attempts to predict a given song’s “potential for success” – for our project, we defined “success” as binary, indicated by whether or not a song ended up on [Billboard’s Hot 100 chart](https://www.billboard.com/charts/hot-100). Previous attempts at solving this problem have used supervised learning over high-level acoustic features (like [Spotify’s “Audio Features”](https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-audio-features)). For our solution, we built a music industry “co-collaborator” network and used the output of a graph auto-encoder as additional training data for a model – this added social component enabled us to achieve 86% accuracy for predicting a song’s success. 

![Architecture of Neural A&R](https://i.imgur.com/3bd7aAp.png)
*A diagram of our methods* 

![The co-collaborator social network](https://i.imgur.com/AjME1EW.png)
*A visualization of the music industry co-collaborator network we built *

Elaboration on our methodologies and results can be found in the final paper! The data we scraped for the project can be found on [this Mega drive](https://mega.nz/folder/0LoxhagD#Ngs65bJk2_m), and the [Jupyter notebook with the final model](https://github.com/tmhubbard/Hit-Song-Predictor/blob/main/Task%203%20-%20Network%20Development/Scripts/Neural%20A%26R%20-%20Hit%20Song%20Prediction%20Network.ipynb) is in Task 3’s Scripts folder. 

Each of the "Task" folders represent distinct portions of this project's workload, including: 
* Task 1: Scraping data from various websites (to be used as training data / the basis of the social network) 
* Task 2: Scripts for creating the music industry co-collaboration network
* Task 3: Creation of the models used to predict hit songs
