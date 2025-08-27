import { useState } from 'react'
import { 
  Title, 
  Card, 
  Button, 
  Group, 
  FileButton,
  Text,
  Select,
  MultiSelect,
  Progress,
  Alert,
  Tabs
} from '@mantine/core'
import { IconUpload, IconRefresh, IconDownload, IconAlertCircle } from '@tabler/icons-react'
import { api } from '../utils/api'

export default function Admin() {
  const [ingestionStatus, setIngestionStatus] = useState<'idle' | 'running' | 'complete' | 'error'>('idle')
  const [ingestionProgress, setIngestionProgress] = useState(0)
  const [selectedSources, setSelectedSources] = useState<string[]>(['osha_establishment', 'news'])
  const [uploadStatus, setUploadStatus] = useState<string>('')

  const dataSources = [
    { value: 'osha_establishment', label: 'OSHA Establishment Search' },
    { value: 'osha_accidents', label: 'OSHA Accident Reports' },
    { value: 'news', label: 'News/RSS Feeds' },
    { value: 'ita', label: 'OSHA ITA Data' }
  ]

  const runIngestion = async () => {
    try {
      setIngestionStatus('running')
      setIngestionProgress(0)
      
      const result = await api.runIngestion({
        sources: selectedSources,
        since: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString() // Last 30 days
      })
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setIngestionProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 500)
      
      setTimeout(() => {
        clearInterval(progressInterval)
        setIngestionProgress(100)
        setIngestionStatus('complete')
        console.log('Ingestion result:', result)
      }, 5000)
      
    } catch (error) {
      setIngestionStatus('error')
      console.error('Ingestion failed:', error)
    }
  }

  const rebuildOpportunities = async () => {
    try {
      await api.rebuildOpportunities()
      alert('Opportunities rebuilt successfully!')
    } catch (error) {
      console.error('Failed to rebuild opportunities:', error)
      alert('Failed to rebuild opportunities')
    }
  }

  const handleFileUpload = async (file: File | null, mappingType: string) => {
    if (!file) return
    
    try {
      setUploadStatus(`Uploading ${mappingType}...`)
      const result = await api.uploadCSV(file, mappingType)
      setUploadStatus(`✅ ${mappingType} uploaded successfully: ${result.processed} records processed`)
    } catch (error) {
      setUploadStatus(`❌ Failed to upload ${mappingType}`)
      console.error('Upload failed:', error)
    }
  }

  return (
    <div>
      <Title order={1} mb="lg">Administration</Title>

      <Tabs defaultValue="ingestion">
        <Tabs.List mb="lg">
          <Tabs.Tab value="ingestion">Data Ingestion</Tabs.Tab>
          <Tabs.Tab value="uploads">File Uploads</Tabs.Tab>
          <Tabs.Tab value="scoring">Scoring Config</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="ingestion">
          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">Manual Data Ingestion</Title>
            
            <MultiSelect
              label="Data Sources"
              placeholder="Select sources to ingest"
              value={selectedSources}
              onChange={setSelectedSources}
              data={dataSources}
              mb="md"
            />

            <Group mb="md">
              <Button 
                onClick={runIngestion}
                loading={ingestionStatus === 'running'}
                leftSection={<IconRefresh size={16} />}
              >
                Run Ingestion
              </Button>
              <Button 
                onClick={rebuildOpportunities}
                variant="light"
                leftSection={<IconRefresh size={16} />}
              >
                Rebuild Opportunities
              </Button>
            </Group>

            {ingestionStatus === 'running' && (
              <div>
                <Text size="sm" mb="xs">Ingesting data from selected sources...</Text>
                <Progress value={ingestionProgress} mb="md" />
              </div>
            )}

            {ingestionStatus === 'complete' && (
              <Alert icon={<IconAlertCircle size={16} />} color="green" mb="md">
                Ingestion completed successfully! Check the Target List for new opportunities.
              </Alert>
            )}

            {ingestionStatus === 'error' && (
              <Alert icon={<IconAlertCircle size={16} />} color="red" mb="md">
                Ingestion failed. Check console for details.
              </Alert>
            )}
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="uploads">
          <Card padding="lg" radius="md" withBorder mb="lg">
            <Title order={3} mb="md">CSV File Uploads</Title>
            <Text size="sm" c="dimmed" mb="md">
              Upload CSV files to populate company relationships and aliases.
            </Text>

            <Group mb="lg">
              <div>
                <Text size="sm" weight={600} mb="xs">Subcontractor Relationships</Text>
                <Text size="xs" c="dimmed" mb="xs">
                  Columns: gc_name, owner_name, sub_name, project_name, location, start_date, end_date, trade, po_value
                </Text>
                <FileButton 
                  onChange={(file) => handleFileUpload(file, 'sub_relationships')} 
                  accept=".csv"
                >
                  {(props) => (
                    <Button {...props} leftSection={<IconUpload size={16} />} variant="light">
                      Upload Relationships CSV
                    </Button>
                  )}
                </FileButton>
              </div>

              <div>
                <Text size="sm" weight={600} mb="xs">Company Aliases</Text>
                <Text size="xs" c="dimmed" mb="xs">
                  Columns: canonical_name, alias
                </Text>
                <FileButton 
                  onChange={(file) => handleFileUpload(file, 'company_aliases')} 
                  accept=".csv"
                >
                  {(props) => (
                    <Button {...props} leftSection={<IconUpload size={16} />} variant="light">
                      Upload Aliases CSV
                    </Button>
                  )}
                </FileButton>
              </div>

              <div>
                <Text size="sm" weight={600} mb="xs">Subcontractor Profiles</Text>
                <Text size="xs" c="dimmed" mb="xs">
                  Columns: sub_name, trade, headcount_bucket, insurance_notes, emr
                </Text>
                <FileButton 
                  onChange={(file) => handleFileUpload(file, 'sub_profile')} 
                  accept=".csv"
                >
                  {(props) => (
                    <Button {...props} leftSection={<IconUpload size={16} />} variant="light">
                      Upload Profiles CSV
                    </Button>
                  )}
                </FileButton>
              </div>
            </Group>

            {uploadStatus && (
              <Alert mb="md">
                <Text size="sm">{uploadStatus}</Text>
              </Alert>
            )}
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="scoring">
          <Card padding="lg" radius="md" withBorder>
            <Title order={3} mb="md">Scoring Configuration</Title>
            <Text size="sm" c="dimmed" mb="md">
              Configure propensity scoring weights and benchmarks.
            </Text>
            
            <Alert icon={<IconAlertCircle size={16} />} color="blue">
              Scoring configuration is managed via the backend config files. 
              See <code>/backend/config/benchmarks.yaml</code> for DART benchmarks and scoring weights.
            </Alert>
          </Card>
        </Tabs.Panel>
      </Tabs>
    </div>
  )
}