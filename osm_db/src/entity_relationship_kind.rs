use rusqlite::types::ToSqlOutput;
use rusqlite::types::{FromSql, FromSqlError, FromSqlResult};
use rusqlite::{types::ValueRef, ToSql};

#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum EntityRelationshipKind {
    OSMChild,
    Street,
    Address,
}

impl ToSql for EntityRelationshipKind {
    fn to_sql(&self) -> Result<ToSqlOutput<'_>, rusqlite::Error> {
        use EntityRelationshipKind::*;
        match self {
            OSMChild => Ok(ToSqlOutput::from(0)),
            Street => Ok(ToSqlOutput::from(1)),
            Address => Ok(ToSqlOutput::from(2)),
        }
    }
}

impl FromSql for EntityRelationshipKind {
    fn column_result(value: ValueRef<'_>) -> FromSqlResult<Self> {
        if let ValueRef::Integer(val) = value {
            match val {
                0 => Ok(EntityRelationshipKind::OSMChild),
                2 => Ok(EntityRelationshipKind::Address),
                1 => Ok(EntityRelationshipKind::Street),
                _ => Err(FromSqlError::OutOfRange(val)),
            }
        } else {
            Err(FromSqlError::InvalidType)
        }
    }
}
