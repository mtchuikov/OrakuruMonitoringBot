# -*- coding: utf-8 -*-
import asyncio
from asyncio import gather

from db.controller import validator_data, leaderboard

from web.methods import request_get

from answer_templates import message

from config import cfg


async def update_validator_table():

    for data_dict in await request_get(cfg.api_validator_data, return_json=True):
        filter_by_address = {'address':data_dict['address']}

        get_validator_data = validator_data.get_row_by_criteria(criteria=filter_by_address)

        if get_validator_data:
            data_dict.pop('address')
            validator_data.upgrade_row_by_criteria(data_dict, criteria=filter_by_address)
        else:
            validator_data.paste_row(data_dict)

    validator_data.commit()


async def update_leaderboard_table():
    leaderboard.delete_all_rows()

    counter = 1; note = ''
    for data in validator_data.get_all_rows():
        counter += 1

        short_address = data.address[0:4] + '...' + data.address[-5:-1]
        note += message.leaderboard_note % (counter, data.address ,short_address, data.score,
                                            data.responses, round(data.response_time, 2))

        if counter % 3 == 0:
            leaderboard.paste_row({'text':note})
            note = ''

    leaderboard.commit()


async def update_data():
    while True:
        await gather(update_validator_table(), update_leaderboard_table())
        await asyncio.sleep(120)
