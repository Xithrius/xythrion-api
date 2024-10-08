import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.models.link_map import LinkMapChannelModel, LinkMapConverterModel


async def test_create_one_link_map_channel_model(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    data = {
        "server_id": 1111,
        "input_channel_id": 2222,
        "output_channel_id": 3333,
    }
    create_data = LinkMapChannelModel(**data)
    dbsession.add(create_data)
    await dbsession.commit()


async def test_create_one_link_map_converter_model_with_to_link(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    data = {
        "from_link": "example_from_link",
        "to_link": "example_to_link",
    }

    create_data = LinkMapConverterModel(**data)

    dbsession.add(create_data)
    await dbsession.commit()

    created_instance = await dbsession.execute(
        select(LinkMapConverterModel).where(LinkMapConverterModel.id == create_data.id),
    )
    fetched_converter = created_instance.scalar()

    assert fetched_converter is not None
    assert fetched_converter.from_link == data["from_link"]
    assert fetched_converter.to_link == data["to_link"]
    assert fetched_converter.xpath is None


async def test_create_one_link_map_to_link_and_xpath_throws_error(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    data = {
        "from_link": "example_from_link",
        "to_link": "example_to_link",
        "xpath": "some/xpath",
    }
    create_data = LinkMapConverterModel(**data)
    dbsession.add(create_data)

    with pytest.raises(IntegrityError):
        await dbsession.commit()


async def test_create_one_link_map_channel_and_multiple_converters(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    channel_data = {
        "server_id": 123,
        "input_channel_id": 456,
        "output_channel_id": 789,
    }
    channel = LinkMapChannelModel(**channel_data)
    dbsession.add(channel)
    await dbsession.commit()

    converters_data = [
        {"from_link": "from_link_1", "to_link": "to_link_1", "xpath": None},
        {"from_link": "from_link_2", "to_link": None, "xpath": "xpath_2"},
    ]

    converters = []
    for converter_data in converters_data:
        converter = LinkMapConverterModel(**converter_data)
        converter.channels.append(channel)
        converters.append(converter)
        dbsession.add(converter)
    await dbsession.commit()

    results = await dbsession.execute(select(LinkMapChannelModel).where(LinkMapChannelModel.id == channel.id))
    stored_channel = results.scalar()
    assert stored_channel is not None
    assert len(stored_channel.converters) == len(converters_data)
    assert stored_channel.server_id == channel_data["server_id"]

    for converter, converter_data in zip(stored_channel.converters, converters_data, strict=False):
        assert converter.from_link == converter_data["from_link"]
        assert converter.to_link == converter_data["to_link"]
        assert converter.xpath == converter_data["xpath"]


async def test_create_one_converter_and_multiple_channels(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    converter_data = {"from_link": "from_link_1", "to_link": "to_link_1", "xpath": None}
    converter = LinkMapConverterModel(**converter_data)
    dbsession.add(converter)
    await dbsession.commit()

    channels_data = [
        {
            "server_id": 123,
            "input_channel_id": 456,
            "output_channel_id": 789,
        },
        {
            "server_id": 111,
            "input_channel_id": 222,
            "output_channel_id": 333,
        },
    ]

    channels = []
    for channel_data in channels_data:
        channel = LinkMapChannelModel(**channel_data)
        channel.converters.append(converter)
        channels.append(channel)
        dbsession.add(channel)
    await dbsession.commit()

    results = await dbsession.execute(select(LinkMapConverterModel).where(LinkMapConverterModel.id == converter.id))
    stored_converter = results.scalar()
    assert stored_converter is not None
    assert len(stored_converter.channels) == len(channels_data)

    for channel, channel_data in zip(stored_converter.channels, channels_data, strict=False):
        assert channel.input_channel_id == channel_data["input_channel_id"]
        assert channel.output_channel_id == channel_data["output_channel_id"]
