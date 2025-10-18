from datetime import datetime
import streamlit as st
import client


def setup_page():
    st.title("⚙️ Setup")
    st.markdown("Configure your API key and select your preferred league and year.")

    st.header("1. API Key Configuration")

    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    with st.container():
        st.info(
            "Enter your Football API key to use the application. You can get started for free at [API-Football](https://www.api-football.com)."
        )

        api_key = st.text_input(
            "Enter your API key:",
            value=st.session_state.get("api_key", ""),
            type="password",
            placeholder="api-sports-key-here",
            key="api_key_input",
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Test API Key", type="primary", use_container_width=True):
                if api_key:
                    try:
                        leagues = client.get_leagues(api_key)
                        st.session_state.api_key = api_key
                        st.success("✅ API Key is valid!")
                    except Exception as e:
                        st.error(f"Invalid API Key: {e}")
                else:
                    st.error("Please enter a valid API key.")

    if st.session_state.get("api_key"):
        st.header("2. League Selection")

        try:
            leagues = client.get_leagues(st.session_state.api_key)
            league_names = [league["league"]["name"] for league in leagues]

            target_league = st.session_state.get("selected_league_name", "NWSL Women")
            default_index = (
                league_names.index(target_league)
                if target_league in league_names
                else 0
            )

            selected_league = st.selectbox(
                "Select a League",
                league_names,
                index=default_index,
                key="league_select",
            )

            selected_league_id = next(
                (
                    league["league"]["id"]
                    for league in leagues
                    if league["league"]["name"] == selected_league
                ),
                None,
            )

            st.session_state.selected_league_name = selected_league
            st.session_state.selected_league_id = selected_league_id

            st.header("3. Year Selection")

            data_years = client.get_league_seasons(st.session_state.api_key)
            current_year = datetime.now().year

            default_year = st.session_state.get("selected_year", current_year)
            default_year_index = (
                data_years.index(default_year) if default_year in data_years else 0
            )

            selected_year = st.selectbox(
                "Select a Year",
                sorted(data_years, reverse=True),
                index=default_year_index,
                key="year_select",
            )

            st.session_state.selected_year = selected_year

            st.success(f"Setup Complete!")
            st.info(f"**League:** {selected_league}\n\n**Year:** {selected_year}")

        except Exception as e:
            st.error(f"Error loading leagues: {e}")


def verify_setup():
    if not all(
        key in st.session_state
        for key in ["api_key", "selected_league_id", "selected_year"]
    ):
        st.warning("⚠️ Please complete the setup first!")
        st.page_link("Setup", icon="⚙️")
        return

    st.success(
        f"✅ Using {st.session_state.selected_league_name} - {st.session_state.selected_year}"
    )


def player_stats_page():
    st.title("📊 Player Stats")

    verify_setup()

    st.header("Select Team")
    teams = client.get_teams(
        st.session_state.api_key,
        st.session_state.selected_league_id,
        st.session_state.selected_year,
    )
    team_names = [team["team"]["name"] for team in teams]
    selected_team = st.selectbox("Select a Team", team_names)

    selected_team_id = next(
        (team["team"]["id"] for team in teams if team["team"]["name"] == selected_team),
        None,
    )

    st.header("Select Player")
    players = client.get_team_players(
        st.session_state.api_key, selected_team_id, st.session_state.selected_year
    )
    player_names = [player["player"]["name"] for player in players]
    selected_player = st.selectbox("Select a Player", player_names)

    selected_player_id = next(
        (
            player["player"]["id"]
            for player in players
            if player["player"]["name"] == selected_player
        ),
        None,
    )

    if selected_player_id:
        player_stats = client.get_player_stats(
            st.session_state.api_key,
            selected_player_id,
            selected_team_id,
            st.session_state.selected_year,
        )

        if player_stats:
            st.header(f"📈 Stats for {selected_player}")
            st.write(player_stats)
        else:
            st.warning("No stats available for this player.")


def fixture_stats_page():
    st.title("📅 Fixture Stats")

    verify_setup()
    st.header("Select Fixture")

    fixtures = client.get_fixtures(
        st.session_state.api_key,
        st.session_state.selected_league_id,
        st.session_state.selected_year,
    )

    finished_fixtures = [
        fixture for fixture in fixtures if fixture["fixture"]["status"]["short"] == "FT"
    ]

    finished_fixtures.sort(key=lambda x: x["fixture"]["date"], reverse=True)

    cleaned_fixtures = [
        f"{fixture['fixture']['date'].split('T')[0]}  {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}"
        for fixture in finished_fixtures
    ]

    st.selectbox("Select a Fixture", cleaned_fixtures)


def main():
    st.set_page_config(
        page_title="Women's Soccer Stats",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "mailto:soccer@cantu.dev",
            "Report a bug": "mailto:soccer@cantu.dev",
            "About": f'Built using Streamlit and deployed using Heroku. \nLast deployed on {datetime.now().strftime("%d/%m/%Y at %H:%M:%S UTC")}',
        },
    )

    pages = {
        "Setup": setup_page,
        "Player Stats": player_stats_page,
        "Fixture Stats": fixture_stats_page,
    }

    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to:", list(pages.keys()))

    pages[selected_page]()


if __name__ == "__main__":
    main()
