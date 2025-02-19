interface ProgressDisplayProps {
    progress: any[]
  }
  
  export default function ProgressDisplay({ progress }: ProgressDisplayProps) {
    return (
      <div className="mt-4">
        <h2 className="text-xl font-semibold mb-2">Progress</h2>
        {progress.map((item, index) => (
          <div key={index} className="mb-2 p-2 border rounded">
            <p>
              <strong>Status:</strong> {item.status}
            </p>
            <p>
              <strong>Filename:</strong> {item.filename}
            </p>
            <p>
              <strong>Message:</strong> {item.message}
            </p>
            {item.data && (
              <div>
                <strong>Data:</strong>
                <pre>{JSON.stringify(item.data, null, 2)}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }
  
  