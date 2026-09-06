/** Creates a FIFO that survives rejection and returns each task's own result. */
export function createSerialQueue() {
  let tail = Promise.resolve();

  return function enqueue<T>(work: () => Promise<T>): Promise<T> {
    const result = tail.then(work);
    tail = result.then(
      () => undefined, // onFulfilled
      () => undefined, // onRejected
    );
    return result;
  };
}
