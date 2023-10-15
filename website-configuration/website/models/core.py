"""Concretely implements the proxy user and taxon interface using SQLAlchemy."""
from flask import session
from typing import List
from flask import render_template
from emikg_interfaces import User as UserInterface
from emikg_interfaces.from_identifier import IdentifierNotFound
from alchemy_wrapper.models import User as UsersTable

from emikg_interfaces import Taxon as TaxonInterface
from alchemy_wrapper.models import Taxon as TaxonTable
from alchemy_wrapper.models import ORCID
from .section import RecordPage, Section, RecordBadge
from ..exceptions import APIException, NotLoggedIn, Unauthorized


class User(UserInterface, RecordPage, Section):
    """Concrete implementation of the user interface using SQLAlchemy."""

    def __init__(self, user: UsersTable):
        """Initialize the user object from a user ID."""
        self._user = user

    @staticmethod
    def from_id(identifier: int) -> "User":
        """Return a user object from a user ID."""
        return User(UsersTable.from_id(identifier))

    @staticmethod
    def from_flask_session() -> "User":
        """Return a user object from the Flask session."""
        try:
            return User.from_id(User.session_user_id())
        except IdentifierNotFound:
            User.logout()

    @staticmethod
    def from_orcid(orcid: str) -> "User":
        """Return a user object from an ORCID.

        Parameters
        ----------
        orcid : str
            ORCID.

        Implementation details
        ----------------------
        The method looks up whether the ORCID exists in the orcid
        table of the database. If it does, we create a new user object
        from the user ID associated with the ORCID. If it does not, then
        we are currently creating a new user. We insert a new user in the
        users table, and return a new user object from the user ID of the
        newly inserted user. In the same transaction, we also insert the
        ORCID in the orcid table alongside the user ID. The transactional
        aspect is important, as it ensures that the ORCID is inserted only
        if the user is successfully inserted.
        Finally, we return a new user object from the user ID of the newly
        inserted user.
        """
        # To execute this operation, the user must not be already logged in.
        if User.is_authenticated():
            raise APIException("User is already logged in.")

        # We check whether the ORCID exists in the orcid table of the database.
        user = ORCID.get_or_insert_user_from_orcid(orcid)

        # We add the user ID to the Flask session.
        session["user_id"] = user.id

        # Finally, we return a new user object from the user ID of the newly
        # inserted user.
        return User.from_id(user.id)

    @staticmethod
    def logout() -> None:
        """Logout the user.

        Implementation details
        ----------------------
        The method removes the user ID from the Flask session.
        """
        session.pop("user_id", None)

    @staticmethod
    def is_authenticated() -> bool:
        """Return whether the user is authenticated."""
        return "user_id" in session

    @staticmethod
    def session_user_id() -> int:
        """Return a user id from the Flask session."""
        if not User.is_authenticated():
            raise NotLoggedIn()
        return session.get("user_id")

    def is_session_user(self) -> bool:
        """Return whether the current user instance is the session user."""
        return self.get_id() == User.session_user_id()

    @staticmethod
    def get_session_user_language() -> str:
        """Return the language of the session user."""
        return session.get("lang", "en")

    @staticmethod
    def must_be_administrator() -> None:
        """Raise ValueError if the user is not an administrator."""
        if not User.from_flask_session().is_administrator():
            raise Unauthorized()

    @staticmethod
    def must_be_moderator() -> None:
        """Raise ValueError if the user is not an moderator."""
        if not User.from_flask_session().is_moderator():
            raise Unauthorized()

    def get_description(self) -> str:
        """Return the user description."""
        return self._user.get_description()
    
    def get_name(self) -> str:
        return self._user.get_name()

    def is_administrator(self) -> bool:
        return self._user.is_administrator()

    def is_moderator(self) -> bool:
        return self._user.is_moderator()

    def delete(self):
        """Delete the user.

        Raises
        ------
        Unauthorized
            If the user is not an administrator.
            If the user requesting the deletion is not the user being deleted.

        Implementative details
        ----------------------
        This method is implemented by deleting the user from the database, i.e.
        by deleting from the "users" table the row whose primary ID is equal
        to the ID of the current user instance.
        """
        # If the current user is NOT the session user, then
        if not self.is_session_user():
            # The current user session must be an administrator
            User.must_be_administrator()

        # If the current user is the session user, or is an administrator,
        # then delete the user from the database
        self._user.delete()

    def get_sections(self) -> List[Section]:
        """Return sections."""
        return [self]
    
    def get_title(self) -> str:
        """Return the title of the user."""
        return self.get_name()
    
    def get_description(self) -> str:
        """Return the description of the user."""
        return self._user.get_description()


class Taxon(Section, RecordPage, TaxonInterface, RecordBadge):
    def __init__(self, taxon: TaxonTable):
        """Initialize the taxon object from a taxon ID."""
        self._taxon = taxon

    @staticmethod
    def from_id(identifier: int) -> "Taxon":
        """Return a taxon object from a taxon ID."""
        return Taxon(TaxonTable.from_id(identifier))

    def get_author(self) -> User:
        """Return the author of the taxon."""
        return User(self._taxon.get_author())

    def get_description(self) -> str:
        """Return the description of the taxon."""
        return self._taxon.get_description()
    
    def get_section_header(self) -> str:
        """Return the user section header."""
        return "Taxons"

    def get_name(self) -> str:
        """Return the name of the taxon."""
        return self._taxon.get_name()
    
    def get_title(self) -> str:
        """Return the title of the taxon."""
        return self.get_name()
    
    def get_record_badge(self) -> str:
        """Return the taxon record badge."""
        return render_template("badge.html", record=self)

    def delete(self):
        """Delete the taxon."""
        user = User.from_flask_session()

        # Either the user is the author of the taxon, or the user is an admin.
        if not user.is_administrator() and not user.is_author_of(self):
            raise Unauthorized()

        self._taxon.delete()