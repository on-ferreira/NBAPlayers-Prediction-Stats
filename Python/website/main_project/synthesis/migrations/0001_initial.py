# Generated by Django 4.2.7 on 2023-11-29 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("location", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("abbreviation", models.CharField(max_length=5)),
                ("head_coach", models.CharField(max_length=255)),
                ("region", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("position", models.CharField(max_length=10)),
                ("height", models.FloatField()),
                ("weight", models.FloatField()),
                ("birth_date", models.DateField()),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="synthesis.team"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GameStatistics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("MP", models.IntegerField()),
                ("FG", models.IntegerField()),
                ("FGA", models.IntegerField()),
                ("FG_percentage", models.FloatField()),
                ("ThreeP", models.IntegerField()),
                ("ThreePA", models.IntegerField()),
                ("ThreeP_percentage", models.FloatField()),
                ("FT", models.IntegerField()),
                ("FTA", models.IntegerField()),
                ("FT_percentage", models.FloatField()),
                ("ORB", models.IntegerField()),
                ("DRB", models.IntegerField()),
                ("TRB", models.IntegerField()),
                ("AST", models.IntegerField()),
                ("STL", models.IntegerField()),
                ("BLK", models.IntegerField()),
                ("TOV", models.IntegerField()),
                ("PF", models.IntegerField()),
                ("PTS", models.IntegerField()),
                ("plus_minus", models.IntegerField()),
                ("BPM", models.IntegerField()),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="synthesis.game"
                    ),
                ),
                (
                    "opp",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opp",
                        to="synthesis.team",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="synthesis.player",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team",
                        to="synthesis.team",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="game",
            name="away_team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="away_team",
                to="synthesis.team",
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="home_team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="home_team",
                to="synthesis.team",
            ),
        ),
    ]
