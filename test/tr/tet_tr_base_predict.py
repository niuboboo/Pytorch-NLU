# !/usr/bin/python
# -*- coding: utf-8 -*-
# @time    : 2021/7/25 9:30
# @author  : Mo
# @function: predict model, 预测模块


# 适配linux
import logging as logger
import sys
import os
path_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
path_sys = os.path.join(path_root, "pytorch_nlu", "pytorch_textregression")
sys.path.append(path_sys)
print(path_root)
print(path_sys)
# os.environ["CUDA_VISIBLE_DEVICES"] = model_config.get("CUDA_VISIBLE_DEVICES", "0")
from trConfig import model_config
from trTools import load_json
from trOffice import Office
from trData import Corpus

from argparse import Namespace


class TextRegressionPredict:
    def __init__(self, path_config, pretrained_model_name_or_path=None, logger=logger):
        """ 初始化 """
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.logger = logger
        self.load_config(path_config)
        self.load_model()

    def load_config(self, path_config):
        """ 加载超参数  """
        config = load_json(path_config)
        self.config = Namespace(**config)
        if self.pretrained_model_name_or_path:
            self.config.pretrained_model_name_or_path = self.pretrained_model_name_or_path
        # if os.environ.get("CUDA_VISIBLE_DEVICES", "-1") == "-1":
        #     self.config.CUDA_VISIBLE_DEVICES = "-1"
        self.config.CUDA_VISIBLE_DEVICES = model_config.get("CUDA_VISIBLE_DEVICES", "")  # os.environ.get("CUDA_VISIBLE_DEVICES", "-1")
        self.real_model_save_path = os.path.split(path_config)[0]
        self.config.model_save_path = self.real_model_save_path
        # 数据预处理 类
        self.corpus = Corpus(config=self.config, logger=self.logger)

    def load_model(self):
        """ 加载模型  """
        self.office = Office(config=self.config, tokenizer=self.corpus.tokenizer, logger=self.logger)
        try:
            self.office.load_model_state()
        except Exception as e:
            self.logger.info("self.office.load_model_state() is wrong, start self.office.load_model()")
            self.office.load_model()

    def process(self, texts):
        """ 数据预处理, process """
        # token 转 idx, 训练集/验证集
        datas_xy, _ = self.corpus.read_texts_from_json(texts, keys=self.config.xy_keys)
        dataset = self.corpus.preprocess(datas_xy, max_len=self.config.max_len)
        return dataset

    def predict(self, texts, rounded=4, use_logits=False):
        """  分类模型预测
        config:
            texts      : List<dict>, inputs of text, eg. {"num_labels":17, "model_type":"BERT"}
            rounded    : int, rounded of float, eg. 3, 4, 6
            use_logits: Bool, only reture logits, eg. True
        Returns:
            res        : List<list>, output of label-score, eg.
        """
        dataset = self.process(texts)
        res = self.office.predict(dataset, rounded=rounded, use_logits=use_logits)
        return res

    def predict_loop(self):
        while 1:
            print("请输入：")
            text = input()
            res = self.predict(text)
            print(res)


if __name__ == "__main__":
    # BERT-base = 8109M
    # path_config = "../output/text_classification/model_ERNIE/tc.config"
    path_config = "../output/text_regression/model_ERNIE/tc.config"
    # path_config = "../output/text_regression/model_BERT/tc.config"

    tcp = TextRegressionPredict(path_config)
    texts = [{"text": "平乐县，古称昭州，隶属于广西壮族自治区桂林市，位于广西东北部，桂林市东南部，东临钟山县，南接昭平，西北毗邻阳朔，北连恭城，总面积1919.34平方公里。"},
             {"text": "平乐县主要旅游景点有榕津千年古榕、冷水石景苑、仙家温泉、桂江风景区、漓江风景区等，平乐县为漓江分界点，平乐以北称漓江，以南称桂江，是著名的大桂林旅游区之一。"},
             {"text": "印岭玲珑，昭水晶莹，环绕我平中。青年的乐园，多士受陶熔。生活自觉自治，学习自发自动。五育并重，手脑并用。迎接新潮流，建设新平中"},
             {"text": "桂林山水甲天下, 阳朔山水甲桂林"},
             {"text": "她不喜欢你"},
             {"text": "不怎么样"},
             {"text": "流水落花, 不不不, 是伤春"},
             ]
    res = tcp.predict(texts)
    print(res)
    # tcp.office.config.model_save_path = tcp.office.config.model_save_path + "_state"
    # tcp.office.save_model_state()

    while True:
        print("请输入:")
        question = input()
        res = tcp.predict([{"text": question}])
        print(res)
        # print([sorted(r.items(), key=lambda x:x[1], reverse=True) for r in res])

