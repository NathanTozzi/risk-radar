import { useState, useEffect } from 'react'
import { 
  Table, 
  Title, 
  Badge, 
  Group, 
  TextInput, 
  Select, 
  Button, 
  Card,
  Text,
  ActionIcon,
  Tooltip
} from '@mantine/core'
import { IconSearch, IconEye, IconDownload } from '@tabler/icons-react'
import { Link } from 'react-router-dom'
import { api } from '../utils/api'
import { TargetOpportunity } from '../types'

export default function TargetList() {
  const [opportunities, setOpportunities] = useState<TargetOpportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [minScore, setMinScore] = useState('30')
  const [stateFilter, setStateFilter] = useState('')
  const [sortBy, setSortBy] = useState('score')

  useEffect(() => {
    fetchOpportunities()
  }, [minScore])

  const fetchOpportunities = async () => {
    try {
      setLoading(true)
      const data = await api.getOpportunities({ 
        min_score: parseInt(minScore),
        limit: 100 
      })
      setOpportunities(data)
    } catch (error) {
      console.error('Failed to fetch opportunities:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredOpportunities = opportunities
    .filter(opp => {
      const companyName = opp.gc?.name || opp.owner?.name || ''
      const matchesSearch = companyName.toLowerCase().includes(search.toLowerCase())
      const matchesState = !stateFilter || 
        (opp.gc?.state === stateFilter) || 
        (opp.owner?.state === stateFilter)
      return matchesSearch && matchesState
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.propensity_score - a.propensity_score
        case 'company':
          const nameA = a.gc?.name || a.owner?.name || ''
          const nameB = b.gc?.name || b.owner?.name || ''
          return nameA.localeCompare(nameB)
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        default:
          return 0
      }
    })

  const getScoreBadgeColor = (score: number) => {
    if (score >= 80) return 'red'
    if (score >= 60) return 'orange'
    if (score >= 40) return 'yellow'
    return 'blue'
  }

  const getConfidenceBadgeColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green'
    if (confidence >= 0.6) return 'yellow'
    return 'gray'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const exportToCsv = () => {
    const headers = ['Company', 'Type', 'Score', 'Driver', 'State', 'Talk Track', 'Date']
    const rows = filteredOpportunities.map(opp => [
      opp.gc?.name || opp.owner?.name || '',
      opp.gc ? 'GC' : 'Owner',
      opp.propensity_score.toFixed(0),
      opp.driver_event?.event_type || '',
      opp.gc?.state || opp.owner?.state || '',
      opp.recommended_talk_track,
      formatDate(opp.created_at)
    ])

    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `target-list-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return <div>Loading target list...</div>
  }

  return (
    <div>
      <Group justify="space-between" mb="lg">
        <Title order={1}>Target List</Title>
        <Button 
          onClick={exportToCsv} 
          leftSection={<IconDownload size={16} />}
          variant="light"
        >
          Export CSV
        </Button>
      </Group>

      <Card padding="lg" radius="md" withBorder mb="lg">
        <Group mb="md">
          <TextInput
            placeholder="Search companies..."
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            leftSection={<IconSearch size={16} />}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="Min Score"
            value={minScore}
            onChange={(value) => setMinScore(value || '30')}
            data={[
              { value: '0', label: 'All scores' },
              { value: '30', label: '30+' },
              { value: '50', label: '50+' },
              { value: '70', label: '70+' },
              { value: '80', label: '80+' }
            ]}
            w={120}
          />
          <Select
            placeholder="State"
            value={stateFilter}
            onChange={(value) => setStateFilter(value || '')}
            data={[
              { value: '', label: 'All states' },
              { value: 'TX', label: 'Texas' },
              { value: 'CA', label: 'California' },
              { value: 'NY', label: 'New York' },
              { value: 'FL', label: 'Florida' }
            ]}
            w={120}
          />
          <Select
            placeholder="Sort by"
            value={sortBy}
            onChange={(value) => setSortBy(value || 'score')}
            data={[
              { value: 'score', label: 'Score' },
              { value: 'company', label: 'Company' },
              { value: 'date', label: 'Date' }
            ]}
            w={120}
          />
        </Group>

        <Text size="sm" c="dimmed">
          {filteredOpportunities.length} opportunities found
        </Text>
      </Card>

      <Card padding="lg" radius="md" withBorder>
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Company</Table.Th>
              <Table.Th>Type</Table.Th>
              <Table.Th>Score</Table.Th>
              <Table.Th>Driver Event</Table.Th>
              <Table.Th>State</Table.Th>
              <Table.Th>Confidence</Table.Th>
              <Table.Th>Talk Track</Table.Th>
              <Table.Th>Last Seen</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {filteredOpportunities.map((opportunity) => {
              const company = opportunity.gc || opportunity.owner
              const companyType = opportunity.gc ? 'GC' : 'Owner'
              
              return (
                <Table.Tr key={opportunity.id}>
                  <Table.Td>
                    <div>
                      <Text weight={600} size="sm">
                        {company?.name || 'Unknown Company'}
                      </Text>
                      <Text size="xs" c="dimmed">
                        {company?.naics}
                      </Text>
                    </div>
                  </Table.Td>
                  <Table.Td>
                    <Badge size="sm" variant="light">
                      {companyType}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge 
                      size="lg" 
                      color={getScoreBadgeColor(opportunity.propensity_score)}
                      variant="filled"
                    >
                      {opportunity.propensity_score.toFixed(0)}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge size="sm" variant="outline">
                      {opportunity.driver_event?.event_type || 'N/A'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>{company?.state || 'N/A'}</Table.Td>
                  <Table.Td>
                    <Badge 
                      size="sm" 
                      color={getConfidenceBadgeColor(opportunity.confidence)}
                      variant="light"
                    >
                      {(opportunity.confidence * 100).toFixed(0)}%
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" style={{ maxWidth: 200 }}>
                      {opportunity.recommended_talk_track}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {formatDate(opportunity.created_at)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Tooltip label="View details">
                      <ActionIcon 
                        component={Link} 
                        to={`/targets/${opportunity.id}`}
                        variant="light"
                        size="sm"
                      >
                        <IconEye size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Table.Td>
                </Table.Tr>
              )
            })}
          </Table.Tbody>
        </Table>

        {filteredOpportunities.length === 0 && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <Text c="dimmed">No opportunities found matching your criteria.</Text>
            <Button 
              mt="md" 
              onClick={() => api.rebuildOpportunities()} 
              variant="light"
            >
              Rebuild Opportunities
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}