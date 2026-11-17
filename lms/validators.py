from rest_framework import serializers
from urllib.parse import urlparse


def validate_youtube_link(value):
    """
    Проверяет, что ссылка ведет только на youtube.com.
    """

    parsed_url = urlparse(value)


    if not parsed_url.netloc:
        raise serializers.ValidationError("Это не похоже на ссылку. Укажите корректный URL.")

    if not parsed_url.netloc.endswith('youtube.com'):
        raise serializers.ValidationError(
            "Ссылки на сторонние ресурсы запрещены. Разрешены только ссылки на youtube.com.")