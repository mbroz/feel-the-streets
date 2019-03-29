#![feature(await_macro, async_await, futures_api)]
use server::{amqp_utils, background_task::BackgroundTask, background_task_constants, Result};
use tokio::await;
use tokio::prelude::*;

use lapin_futures::channel::{BasicConsumeOptions, QueueDeclareOptions};
use lapin_futures::queue::Queue;
use lapin_futures::types::FieldTable;
use log::{info, error};

async fn consume_tasks_real() -> Result<()> {
    use background_task_constants::*;
    let client = await!(amqp_utils::connect_to_broker())?;
    await!(amqp_utils::init_background_job_queues(&client))?;
    let channel = await!(client.create_channel())?;
    let opts = QueueDeclareOptions{passive: true, ..Default::default()};
    let count = await!(channel.queue_declare(&background_task_constants::FUTURE_TASKS_QUEUE, opts, FieldTable::new()))?.message_count();
    if count == 0 {
        info!("Initially scheduling the databases update task...");
        BackgroundTask::UpdateAreaDatabases.deliver_at_time(DATABASES_UPDATE_HOUR, DATABASES_UPDATE_MINUTE, DATABASES_UPDATE_SECOND);
    }
    let queue = Queue::new(background_task_constants::TASKS_QUEUE.to_string(), 0, 0);
    let mut consumer = await!(channel.basic_consume(
        &queue,
        "tasks_consumer",
        BasicConsumeOptions::default(),
        FieldTable::new()
    ))?;
    while let Some(msg) = await!(consumer.next()) {
        let msg = msg?;
        let task: BackgroundTask = serde_json::from_slice(&msg.data)?;
        task.execute()?;
    }
    Ok(())
}

async fn consume_tasks() {
    if let Err(e) = await!(consume_tasks_real()) {
        error!("Error during task consumption: {}", e);
    }
}

fn main() -> Result<()> {
    env_logger::init();
    let _dotenv_path = dotenv::dotenv()?;
    tokio::run_async(consume_tasks());
    Ok(())
}
