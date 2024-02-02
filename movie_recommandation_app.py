import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from scipy.io import mmwrite, mmread
from gensim.models import Word2Vec
import pickle
from PyQt5.QtCore import QStringListModel

form_window = uic.loadUiType('./movie_recommandation.ui')[0]

class Exam(QWidget,form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Tfidf_matrix = mmread('./models/Tfidf_movie_review.mtx').tocsr()
        with open('./models/tfidf.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)
        self.embedding_model = Word2Vec.load('./models/word2vec_movie_review.model')
        self.df_reviews = pd.read_csv('cleaned_one_review.csv')
        self.titles = list(self.df_reviews['titles'])
        self.titles.sort()
        for title in self.titles:
            self.comboBox.addItem(title)

        self.comboBox.currentIndexChanged.connect(self.combobox_slot)
        self.btn_recommandation.clicked.connect(self.btn_slot)
        model = QStringListModel()
        model.setStringList(self.titles)
        completer = QCompleter()
        completer.setModel(model)
        self.le_keyword.setCompleter(completer)

    def btn_slot(self):
        key_word = self.le_keyword.text()
        if key_word in self.titles:
            recommandation = self.recommandation_by_movie_title(key_word)
        else:
            recommandation = self.recommandation_by_keyword(key_word)
        if recommandation:
            self.lbl_recommandation.setText(recommandation)

    def combobox_slot(self):
        title = self.comboBox.currentText()
        recommandation = self.recommandation_by_movie_title(title)
        self.lbl_recommandation.setText(recommandation)

    def recommandation_by_keyword(self, key_word):
        try:
            sim_word = self.embedding_model.wv.most_similar(key_word, topn=10)
        except:
            self.lbl_recommandation.setText('없는 단어다')
            return 0
        words = [key_word]
        for word, _ in sim_word:
            words.append(word)
        sentence = []
        count = 10
        for word in words:
            sentence = sentence + [word] * count
            count -= 1
        sentence = ' '.join(sentence)
        sentence_vec = self.Tfidf.transform([sentence])
        cosine_sim = linear_kernel(sentence_vec, self.Tfidf_matrix)
        recommendation = self.getRecommendation(cosine_sim)
        recommandation = '\n'.join(list(recommandation))
        return recommendation
    def recommandation_by_movie_title(self, title):
        movie_idx = self.df_reviews[self.df_reviews['titles'] == title].index[0]
        cosine_sim = linear_kernel(self.Tfidf_matrix[movie_idx], self.Tfidf_matrix)
        recommandation = self.getRecommendation(cosine_sim)
        recommandation = '\n'.join(list(recommandation))
        return recommandation

    def getRecommendation(self, cosine_sim):
        simScore = list(enumerate(cosine_sim[-1]))
        simScore = sorted(simScore, key=lambda x: x[1], reverse=True)
        simScore = simScore[:11]
        movieIdx = [i[0] for i in simScore]
        recmovieList = self.df_reviews.iloc[movieIdx, 0]
        return recmovieList[1:11]

if __name__ =='__main__':
    app =QApplication(sys.argv)
    mainWindow=Exam()
    mainWindow.show()
    sys.exit(app.exec_())