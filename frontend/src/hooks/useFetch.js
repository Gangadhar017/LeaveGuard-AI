import { useCallback, useEffect, useRef, useState } from 'react'
import { getApiError } from '../api/client.js'

/**
 * Small data-fetching hook with loading / error state and a retry function.
 */
export default function useFetch(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const load = useCallback(async (silent = false) => {
    if (!silent) setLoading(true)
    setError(null)
    try {
      const response = await fetcherRef.current()
      setData(response.data)
      return response.data
    } catch (err) {
      setError(getApiError(err))
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { data, loading, error, reload: load }
}
