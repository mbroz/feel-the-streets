use anyhow::Result;
use std::fs;
use std::convert::TryInto;
use osm_db::AreaDatabase;
use server::area::{Area, AreaState};
use diesel::{SqliteConnection, Connection};

const FROZEN_OSM_ID_OFFSET: i64 = 20_000_000_000;

pub fn create_frozen_copy(area_id: i64, new_name: String) -> Result<()> {
    let frozen_id =area_id + FROZEN_OSM_ID_OFFSET;
    let orig_path = AreaDatabase::path_for(area_id, true);
    let new_path = AreaDatabase::path_for(frozen_id, true);
    println!("Copying the area database...");
    fs::copy(&orig_path, &new_path)?;
println!("Copied, creating the database record...");
    let db_conn = SqliteConnection::establish("server.db")?;
let mut new_area = Area::create(frozen_id, &new_name, &db_conn)?;
new_area.state = AreaState::Frozen;
new_area.db_size = fs::metadata(new_path)?.len().try_into().unwrap();
new_area.save(&db_conn)?;
println!("Successfully created a frozen copy of area {} with new name {} and id {}.", area_id, new_name, frozen_id);
    Ok(())
}