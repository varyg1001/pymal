__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from pymal import exceptions


class Recommendation:
    """
    Recommendation holds all the data from a recommendation in MAL about an anime.

    :ivar recommended_anime: :class:`anime.Anime`
    :ivar recommends: :class:`dict`
    """

    def __init__(self, div):
        """
        :param div: The dic of the recommendation to parse all the data from it.
        :type div: bs4.element.Tag
        """
        from pymal import account, anime

        recommended, recommends_divs = div.table.tbody.tr.findAll(
            name="td", recursive=False
        )

        self.recommended_anime = anime.Anime(int(recommended.div.a["href"].split("/")[2]))

        data = recommends_divs.findAll(name="div", recursive=False)
        if len(data) == 3:
            recommends = [data[2]]
        elif len(data) == 5:
            _, _, first_recommend, _, other_recommends = data
            recommends = [first_recommend] + other_recommends.findAll(
                name="div", recursive=False
            )
        else:
            raise exceptions.FailedToReloadError(
                "Unknown size of data: " + str(len(data))
            )

        self.recommends = {}

        for recommend in recommends:
            recommend_data, user_data = recommend.findAll(name="div", recursive=False)
            username = user_data.find(name="a", recursive=False)["href"].split("/")[2]
            self.recommends[account.Account(username)] = recommend_data.text

    def __repr__(self):
        return f"<{self.__class__.__name__:s} for {self.recommended_anime:s} by {len(self.recommends):d} users>"
