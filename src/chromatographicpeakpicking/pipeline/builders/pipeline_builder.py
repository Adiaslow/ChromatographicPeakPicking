# src/chromatographicpeakpicking/pipeline/builders/pipeline_builder.py


class PipelineBuilder:
    def __init__(self):
        self.pipeline = AnalysisPipeline()

    def add_analyzable(self, analyzable):
        self.pipeline.add_analyzable(analyzable)
        return self

    def add_corrector(self, corrector):
        self.pipeline.add_corrector(corrector)
        return self

    def add_detector(self, detector):
        self.pipeline.add_detector(detector)
        return self

    def add_analyzable(self, analyzable):
        self.pipeline.add_analyzable(analyzable)
        return self

    def add_processor(self, processor):
        self.pipeline.add_processor(processor)
        return self

    def add_selector(self, selector):
        self.pipeline.add_selector(selector)
        return self

    def add_visualizable(self, visualizable):
        self.pipeline.add_visualizable(visualizable)
        return self

    def add_serializable(self, serializable):
        self.pipeline.add_serializable(serializable)
        return self

    def build(self):
        return self.pipeline
