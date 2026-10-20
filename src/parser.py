

class Parser():
    def __init__(self) -> None:
        self.index = Index()
        self.search = Search()
        self.search_dataset = SearchDataSet()
        self.answer = Answer()
        self.answer_dataset = AnswerDataSet()
        self.evaluate = Evaluate()
