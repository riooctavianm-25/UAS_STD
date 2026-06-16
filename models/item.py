class Item:
    """Represent a book/manga/komik item."""
    
    def __init__(self, item_id: int, title: str, item_type: str, author: str, genres: list, description: str):
        """Initialize item."""
        self.id = item_id
        self.title = title.strip()
        self.type = item_type.strip()
        self.author = author.strip()
        self.genres = genres
        self.description = description.strip()

    def summary(self):
        """Get one-line summary of item."""
        return f"[{self.id}] {self.title} ({self.type}) by {self.author}"

    def detail(self):
        """Get full details of item."""
        genre_list = ', '.join(self.genres) if self.genres else 'N/A'
        return (
            f"ID       : {self.id}\n"
            f"Title    : {self.title}\n"
            f"Type     : {self.type}\n"
            f"Author   : {self.author}\n"
            f"Genres   : {genre_list}\n"
            f"Desc     : {self.description}\n"
        )
