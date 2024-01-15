import modules.scripts
from modules import shared, call_queue
import gradio as gr
from video_extras_tab.process import process
from dataclasses import dataclass
from typing import Any


@dataclass
class Components:
    pathIn : Any = None
    fps : Any = None
    pathOut : Any = None


COMPONENTS = Components()


def addTabIntoExtras(component, **kwargs):
    global COMPONENTS
    elem_id = kwargs.get('elem_id', None)
    if elem_id != 'extras_batch_directory_tab':
        return
    batch_from_directory = component
    blockExtras = batch_from_directory.parent.parent.parent.parent
    tabIndex = blockExtras.children[1]
    tabsExtras = batch_from_directory.parent

    with tabsExtras:
        with gr.TabItem('Video', id="extras_video", elem_id="extras_video") as tab_video:
            COMPONENTS.pathIn = gr.Textbox(
                label="Input video",
                placeholder="A video on the same machine where the server is running.",
                elem_id="replacer_input_video")
            COMPONENTS.fps = gr.Slider(
                label='FPS', value=10.0, min=0.0, step=0.1, max=60.0,
                info="(0 = fps from input video)",
                elem_id="replacer_video_fps")
            COMPONENTS.pathOut = gr.Textbox(
                label="Output directory",
                **shared.hide_dirs,
                placeholder="Leave blank to save images to the default path.",
                info='(default is the same directory with input video. Rusult is in "output_seed" subdirectory)',
                elem_id="replacer_output_batch_dir")

    tab_video.select(fn=lambda: 3, inputs=[], outputs=[tabIndex])


def wrapExtrasSubmitButton(component, **kwargs):
    global COMPONENTS
    elem_id = kwargs.get('elem_id', None)
    if elem_id != 'extras_generate':
        return
    submitButton = component
    oldClick = submitButton.click
    def newClick(**kwargs):
        fn=kwargs['fn']
        def wrapper(taskId, pathIn, fps, pathOut, *args, **kwargs):
            return process(taskId, pathIn, fps, pathOut, fn, *args, **kwargs)
        kwargs['fn'] = call_queue.wrap_gradio_call(wrapper, extra_outputs=[None, ''])
        kwargs['inputs'] = [kwargs['inputs'][0]] + [COMPONENTS.pathIn, COMPONENTS.fps,
                    COMPONENTS.pathOut] + kwargs['inputs'][1:]
        return oldClick(**kwargs)
    submitButton.click = newClick


modules.scripts.script_callbacks.on_after_component(addTabIntoExtras)
modules.scripts.script_callbacks.on_after_component(wrapExtrasSubmitButton)

