from src.backend.domain.shared.errors import DomainError


class BlogPostNoCategoryError(DomainError):
    """Вызывается при попытке опубликовать пост без категории"""


class BlogPostNoContentError(DomainError):
    """Вызывается при попытке опубликовать пост с пустым контентом"""


class BlogPostInvalidSlugError(DomainError):
    """Вызывается когда slug не соответствует формату"""


class BlogPostAlreadyPublishedError(DomainError):
    """Вызывается при попытке опубликовать уже опубликованный пост"""
