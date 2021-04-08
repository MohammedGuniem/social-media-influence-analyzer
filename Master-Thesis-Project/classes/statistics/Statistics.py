import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import time


class Statistics:
    def __init__(self, mongo_db_connector, neo4j_db_connector):
        self.mongo_db_connector = mongo_db_connector
        self.neo4j_db_connector = neo4j_db_connector

    def getCrawlingRuntimes(self, network_name, submissions_type, from_date):
        from_date = time.mktime(datetime.datetime. strptime(
            from_date, '%Y-%m-%d').timetuple())

        runtimes = self.mongo_db_connector.getCrawlingRuntimes(
            network_name, submissions_type, from_date)

        runtimes_df = pd.DataFrame(runtimes)
        runtimes_df["date"] = pd.to_datetime(
            runtimes_df['timestamp'], unit='s')
        runtimes_df['date'] = pd.to_datetime(
            runtimes_df['date'], format="%d.%m.%y").astype(dtype="string")

        runtimes_df.drop(['timestamp', '_id', 'network_name',
                          'submissions_type'], axis=1, inplace=True)

        runtimes_df["per group"] = runtimes_df["groups_crawling_time"] / \
            runtimes_df["groups_count"]
        runtimes_df["per submission"] = runtimes_df["submissions_crawling_time"] / \
            runtimes_df["submissions_count"]
        runtimes_df["per comment"] = runtimes_df["comments_crawling_time"] / \
            runtimes_df["comments_count"]

        runtimes_df.set_index(runtimes_df['date'], inplace=True)
        runtimes_df.rename(
            columns={'groups_crawling_time': 'groups', 'submissions_crawling_time': 'submissions', 'comments_crawling_time': 'comments'}, inplace=True)

        fig, axes = plt.subplots(1, 2)

        runtimes_df[["date", "per group", "per submission", "per comment"]].plot(
            kind="area", stacked=True, ax=axes[0], rot=90, fontsize=6, title="Average Crawling runtimes").set(ylabel='seconds')

        runtimes_df[["date", "groups", "submissions", "comments"]].plot(
            kind="area", stacked=True, ax=axes[1], rot=90, fontsize=6, title="Total Crawling runtimes").set(ylabel='seconds')

        fig.suptitle('Crawling Runtimes Statistics')

        plt.show()

    def getInfluenceArea(self, network_name, submissions_type, model_date):
        groups = self.mongo_db_connector.getGroups(network_name)

        submissions = []
        for group in groups:
            group_submissions = self.mongo_db_connector.getSubmissionsOnGroup(
                network_name, submissions_type, group['id'])
            submissions += group_submissions

        groups_df = pd.DataFrame(groups).rename(
            columns={'id': 'group_id'}).drop(['_id'], axis=1)

        submissions_df = pd.DataFrame(submissions).drop(['_id'], axis=1)

        submissions_df = pd.merge(submissions_df, groups_df,
                                  how='outer', on=['group_id'])

        fig, axes = plt.subplots(1, 3)

        submissions_df.groupby("display_name")["display_name"].count().plot(
            kind="pie", ax=axes[0], title="Crawled Groups", autopct='%1.1f%%').axis("off")

        neo4j_graph = self.neo4j_db_connector.get_graph(
            network_name=network_name, date=model_date, relation_type="Influences")

        groups = []
        predicted_influence = []
        for link in neo4j_graph["links"]:
            predicted_influence += link["props"]["influence_areas"]
            groups += link["props"]["groups"]

        groups_df = pd.DataFrame(
            groups, columns=["groups"])

        groups_df.groupby("groups")[
            "groups"].count().plot(kind="pie", ax=axes[1], title="Modelled Groups", autopct='%1.1f%%').axis("off")

        predicted_influence_df = pd.DataFrame(
            predicted_influence, columns=["predicted_influence"])

        predicted_influence_df.groupby("predicted_influence")[
            "predicted_influence"].count().plot(kind="pie", ax=axes[2], title="Predicted Influence Areas", autopct='%1.1f%%').axis("off")

        fig.suptitle(
            'Crawled Subreddits vs. Predicted Influence Area vs. Modelled Subreddits')

        plt.show()

    def getInfluenceScore(self, network_name, submissions_type, model_date, score_type):
        neo4j_graph = self.neo4j_db_connector.get_graph(
            network_name=network_name, date=model_date, relation_type="Influences")

        if score_type:
            score_types = [score_type]
            fig, axes = plt.subplots(2, 1)
            fig.suptitle(F"Influence Scores Distribution using {score_type}")
        else:
            score_types = ["interaction", "activity", "upvotes", "interaction_and_activity",
                           "activity_and_upvotes", "interaction_and_upvotes", "total"]
            fig, axes = plt.subplots(2, 7, figsize=(24, 10))
            fig.tight_layout(pad=4.0)
            fig.suptitle("Influence Scores Distribution")

        axes = axes.ravel()

        links = {}
        for score_type in score_types:
            links[F"{score_type}"] = []
            for link in neo4j_graph["links"]:
                links[F"{score_type}"].append(link['props'][F"{score_type}"])

        links_df = pd.DataFrame(links)

        for score_type in score_types:
            links_df[F"{score_type}"].plot(
                kind="box",
                ax=axes[score_types.index(score_type)],
                title=F"{score_type} score",
                vert=False
            )
            y_axis = axes[score_types.index(score_type)].axes.get_yaxis()
            y_axis.set_visible(False)

            links_df[F"{score_type}"].plot(
                kind="hist",
                bins=links_df[F"{score_type}"].nunique(),
                ax=axes[score_types.index(score_type)+len(score_types)],
                title=F"{score_type} score",
                xticks=links_df[F"{score_type}"],
                rot=90
            )

        plt.show()
