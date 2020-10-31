use rusqlite::ToSql; 
use rusqlite::types::ToSqlOutput;

pub enum EntityRelationshipKind {
    OSMChild
}

impl ToSql for EntityRelationshipKind {
    fn to_sql(&self) -> Result<ToSqlOutput<'_>, rusqlite::Error> {
        use EntityRelationshipKind::*;
        match self {
            OSMChild => Ok(ToSqlOutput::from(0)),
        }
    }
}