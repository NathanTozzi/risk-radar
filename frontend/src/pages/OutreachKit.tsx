import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { 
  Title, 
  Card, 
  Text, 
  Tabs, 
  Button, 
  Group,
  CopyButton,
  ActionIcon,
  Tooltip
} from '@mantine/core'
import { IconCopy, IconDownload, IconCheck } from '@tabler/icons-react'
import { api } from '../utils/api'
import { OutreachKit as OutreachKitType } from '../types'

export default function OutreachKit() {
  const { id } = useParams<{ id: string }>()
  const [outreachKit, setOutreachKit] = useState<OutreachKitType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      fetchOutreachKit(parseInt(id))
    }
  }, [id])

  const fetchOutreachKit = async (kitId: number) => {
    try {
      setLoading(true)
      const data = await api.getOutreachKit(kitId)
      setOutreachKit(data)
    } catch (error) {
      console.error('Failed to fetch outreach kit:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportProspectPack = async () => {
    if (!id) return
    
    try {
      const blob = await api.exportProspectPack(parseInt(id))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `prospect-pack-${id}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export prospect pack:', error)
    }
  }

  if (loading) {
    return <div>Loading outreach kit...</div>
  }

  if (!outreachKit) {
    return <div>Outreach kit not found</div>
  }

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <Title order={1}>Outreach Kit</Title>
        <Button 
          onClick={exportProspectPack}
          leftSection={<IconDownload size={16} />}
        >
          Export Prospect Pack (PDF)
        </Button>
      </Group>

      <Tabs defaultValue="email">
        <Tabs.List mb="lg">
          <Tabs.Tab value="email">Email</Tabs.Tab>
          <Tabs.Tab value="linkedin">LinkedIn DM</Tabs.Tab>
          <Tabs.Tab value="call">Call Notes</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="email">
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Title order={3}>Email Template</Title>
              <CopyButton value={outreachKit.email_md}>
                {({ copied, copy }) => (
                  <Tooltip label={copied ? 'Copied' : 'Copy'} withArrow position="right">
                    <ActionIcon color={copied ? 'teal' : 'gray'} onClick={copy}>
                      {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
                    </ActionIcon>
                  </Tooltip>
                )}
              </CopyButton>
            </Group>
            <div style={{ 
              whiteSpace: 'pre-wrap', 
              backgroundColor: '#f8f9fa', 
              padding: '1rem', 
              borderRadius: '4px',
              fontFamily: 'monospace'
            }}>
              {outreachKit.email_md || 'Email template not generated'}
            </div>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="linkedin">
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Title order={3}>LinkedIn DM Template</Title>
              <CopyButton value={outreachKit.linkedin_md}>
                {({ copied, copy }) => (
                  <Tooltip label={copied ? 'Copied' : 'Copy'} withArrow position="right">
                    <ActionIcon color={copied ? 'teal' : 'gray'} onClick={copy}>
                      {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
                    </ActionIcon>
                  </Tooltip>
                )}
              </CopyButton>
            </Group>
            <div style={{ 
              whiteSpace: 'pre-wrap', 
              backgroundColor: '#f8f9fa', 
              padding: '1rem', 
              borderRadius: '4px',
              fontFamily: 'monospace'
            }}>
              {outreachKit.linkedin_md || 'LinkedIn template not generated'}
            </div>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="call">
          <Card padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="md">
              <Title order={3}>Call Notes</Title>
              <CopyButton value={outreachKit.call_notes_md}>
                {({ copied, copy }) => (
                  <Tooltip label={copied ? 'Copied' : 'Copy'} withArrow position="right">
                    <ActionIcon color={copied ? 'teal' : 'gray'} onClick={copy}>
                      {copied ? <IconCheck size={16} /> : <IconCopy size={16} />}
                    </ActionIcon>
                  </Tooltip>
                )}
              </CopyButton>
            </Group>
            <div style={{ 
              whiteSpace: 'pre-wrap', 
              backgroundColor: '#f8f9fa', 
              padding: '1rem', 
              borderRadius: '4px',
              fontFamily: 'monospace'
            }}>
              {outreachKit.call_notes_md || 'Call notes not generated'}
            </div>
          </Card>
        </Tabs.Panel>
      </Tabs>
    </div>
  )
}