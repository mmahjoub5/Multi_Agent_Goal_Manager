import uuid
from pydantic import UUID4, BaseModel, Field
from pymongo import errors
from typing import Generic, Type, TypeVar
from  backend.app.db.mongo import connection
from  backend.app.configs.config import DATABASE_NAME
from abc import ABC


_database = connection.get_database(DATABASE_NAME)

T = TypeVar("T", bound="NoSQLBaseDocument")

class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    id: UUID4 = Field(default_factory=uuid.uuid4)

    def __eq__(self, value: object) -> bool:
        """
        Check equality between this document and another object.
        Two documents are considered equal if they are of the same class and have the same `id`.

        Args:
            value (object): The object to compare.

        Returns:
            bool: True if the objects are equal, False otherwise.
        """
        if not isinstance(value, self.__class__):
            return False

        return self.id == value.id

    def __hash__(self) -> int:
        """
        Generate a hash based on the `id` field for use in hash-based collections.

        Returns:
            int: The hash value of the document.
        """
        return hash(self.id)
    
    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """
        Convert a MongoDB document into a Pydantic model instance.
        Transforms the MongoDB `_id` field into the model's `id`.

        Args:
            data (dict): The MongoDB document.

        Returns:
            T: An instance of the class populated with the document data.

        Raises:
            ValueError: If the provided data is empty.
        """

        if not data:
            raise ValueError("Data is empty.")

        id = data.pop("_id")

        return cls(**dict(data, id=id))
    
    def to_mongo(self: T, **kwargs) -> dict:
        """
        Convert the Pydantic model instance into a MongoDB-compatible dictionary.
        Transforms the `id` field into MongoDB's `_id` field and converts UUIDs to strings.

        Args:
            **kwargs: Additional arguments for Pydantic's model_dump.

        Returns:
            dict: A dictionary representation suitable for MongoDB.
        """
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        parsed = self.model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)
        
        return parsed
    
    def model_dump(self: T, **kwargs) -> dict:
        """
        Override Pydantic's model_dump to ensure UUID fields are converted to strings.

        Args:
            **kwargs: Additional arguments for Pydantic's model_dump.

        Returns:
            dict: A dictionary representation of the model.
        """
        dict_ = super().model_dump(**kwargs)

        for key, value in dict_.items():
            if isinstance(value, uuid.UUID):
                dict_[key] = str(value)

        return dict_
    
    def save(self: T, **kwargs) -> T | None:
        """
        Save the current document instance to MongoDB.

        Args:
            **kwargs: Additional arguments for the `to_mongo` method.

        Returns:
            T | None: The saved document if successful, otherwise None.
        """
        collection = _database[self.get_collection_name()]
        try:
            collection.insert_one(self.to_mongo(**kwargs))

            return self
        except errors.WriteError:
            print("Failed to insert document.")

            return None
    
    @classmethod
    def create(cls: Type[T], filter_doc:T | dict) -> T:
        """
        Create and save a new document in the database.

        Args:
            data (T | dict): Data to create the document. Can be a dictionary or an instance of the class.

        Returns:
            T: The newly created document instance.

        Raises:
            ValueError: If the provided data is invalid.
            RuntimeError: If saving the document fails.
        """
        collection = _database[cls.get_collection_name()]
        if isinstance(filter_doc, cls):
            filter_doc = filter_doc.to_mongo(exclude_unset=True)
        elif filter_doc is None:
            filter_doc = {}
        try: 
            new_instance = cls(**filter_doc)
            new_instance = new_instance.save()
            if new_instance:
                return new_instance
            if not new_instance:
                raise RuntimeError("Failed to save the new document to the database.")
        except errors.OperationFailure as e:
            raise RuntimeError("Failed to save the new document to the database.")

    @classmethod
    def get_or_create(cls: Type[T], filter_doc:T | dict, **filter_options) -> T:
        """
        Fetch an existing document or create a new one if it doesn't exist.

        Args:
            db: The database connection object.
            filter_doc: An instance of the document or a dictionary to use as filter options.
            **filter_options: Additional filter options to combine with `filter_doc`.

        Returns:
            T: The fetched or newly created document.

        Raises:
            errors.OperationFailure: If a database operation fails.
        """
        collection = _database[cls.get_collection_name()]

        if isinstance(filter_doc, cls):
            filter_doc = filter_doc.to_mongo(exclude_unset=True)
        elif filter_doc is None:
            filter_doc = {}

        combined_filter = {**filter_doc, **filter_options}
        try:
            instance = collection.find_one(combined_filter)
            if instance:
                return cls.from_mongo(instance)

            new_instance = cls(**combined_filter)
            new_instance = new_instance.save()
            if new_instance:
                return new_instance
            
            if new_instance is None:
                raise RuntimeError("Failed to save the new document to the database.")

        except errors.OperationFailure as e:
            print(f"Failed to retrieve document with filter options: {combined_filter}")

            raise e
    
    @classmethod
    def bulk_insert(cls: Type[T], documents: list[T], **kwargs) -> bool:
        collection = _database[cls.get_collection_name()]
        try:
            collection.insert_many(doc.to_mongo(**kwargs) for doc in documents)

            return True
        except (errors.WriteError, errors.BulkWriteError):
            print(f"Failed to insert documents of type {cls.__name__}")

            return False

    @classmethod
    def find(cls: Type[T], **filter_options) -> T | None:
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            return None
        except errors.OperationFailure:
            print("Failed to retrieve document")

            return None

    @classmethod
    def bulk_find(cls: Type[T],  **filter_options) -> list[T]:
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            documents = []
            for instance in list(instances):
                document = cls.from_mongo(instance)
                if document is not None:
                    documents.append(document)
            return documents
        except errors.OperationFailure:
            print("Failed to retrieve documents")

            return []
        
    @classmethod
    def find_all(cls: Type[T],  **filter_options) -> list[T]:
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find({})
            documents = []
            for instance in list(instances):
                document = cls.from_mongo(instance)
                if document is not None:
                    documents.append(document)
            return documents
        except errors.OperationFailure:
            print("Failed to retrieve documents")

            return []

    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise (
                "Document should define an Settings configuration class with the name of the collection."
            )
        return cls.Settings.name
    
    @classmethod
    def remove_document(cls:Type[T], **filter_options) :
        """Remove a document from the MongoDB collection based on filter options.

        Args:
            **filter_options: Key-value pairs to filter the document(s) to be deleted.

        Returns:
            int: The number of documents deleted (0 or 1 for delete_one).
        """
        collection = _database[cls.get_collection_name()]
        try:
            result = collection.delete_one(filter=filter_options)
            return result.deleted_count
        except errors.OperationFailure:
            print("Failed to retrieve documents")
            return 0
        
    @classmethod 
    def update_document(cls:Type[T], filter:dict, update:dict, **kwargs):
        """
        Update documents in the collection based on a filter and update query.

        Args:
            filter (dict): The filter query to match documents.
            update (dict): The update operation to perform.
            **kwargs: Additional options for the update operation.

        Returns:
            int: The number of documents updated.
        """
        collection = _database[cls.get_collection_name()]
        try:
            result = collection.update_one(filter=filter, update=update)
            return result.modified_count
        except errors.OperationFailure as e:
            raise RuntimeError(f"Failed to update documents: {e}")