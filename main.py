"""
Run this file
"""
import uvicorn

from src import helpers
from settings import config
from settings.app import app

from threading import Thread
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory='templates')
app.mount('/images', StaticFiles(directory='images'), name='images')


@app.get('/', response_class=HTMLResponse)
def index(request: Request, view=None):
    """ Returns rendered HTML """

    try:
        if view == 'example':
            example_data = helpers.get_example_calculations()
            _page = templates.TemplateResponse(name='calculations.html',
                                               context={'request': request, 'data': example_data})
            image_path = str(example_data.get('chart_image_path'))
            Thread(target=helpers.delete_render_image, args=(image_path,)).start()
        elif view == 'random':
            example_data = helpers.get_random_calculations()
            _page = templates.TemplateResponse(name='calculations.html',
                                               context={'request': request, 'data': example_data})
            image_path = str(example_data.get('chart_image_path'))
            Thread(target=helpers.delete_render_image, args=(image_path,)).start()
        else:
            _page = templates.TemplateResponse(name='index.html',
                                               context={'request': request, 'data': {}})
        return _page
    except Exception as e:
        return f'An error occured:\n\n{e}'


@app.post('/', response_class=HTMLResponse)
async def show_calculations(request: Request):
    """ Returns rendered HTML """

    try:
        _request_form = await request.form()
        _form_data = _request_form.__dict__.get('_dict', {})

        trading_calculations = helpers.TradingStrategyOne(
            pair=_form_data.get('pair').upper(),
            timeframe=_form_data.get('timeframe'),
            candles_number=_form_data.get('candles'),
            sma_diapason=int(_form_data.get('ma')),
            sl_percent=int(_form_data.get('sl')),
            tp_percent=int(_form_data.get('tp'))
        ).get_trades()
        trading_calculations.update({'calculations_data': _form_data})

        _page = templates.TemplateResponse(name='calculations.html',
                                           context={'request': request, 'data': trading_calculations})
        image_path = str(trading_calculations.get('chart_image_path'))
        Thread(target=helpers.delete_render_image, args=(image_path,)).start()
        return _page
    except Exception as e:
        return f'An error occured:\n\n{e}'


def start():
    """ Starts webserver with uvicorn """
    uvicorn.run(app, host=config.APP_HOST, port=int(config.APP_PORT))


start()
