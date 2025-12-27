"use client"

import { useState, useEffect, useRef } from "react"
import { getStorageStats, type StorageStats } from "../api/stats"

// Цвета для категорий
const CATEGORY_COLORS = {
  audio: "#3B82F6",    // синий
  video: "#EF4444",    // красный
  images: "#10B981",   // зеленый
  documents: "#F59E0B", // желтый
  other: "#8B5CF6"     // фиолетовый
}

// Цвета для диаграммы свободного места
const STORAGE_COLORS = {
  used: "#3B82F6",     // синий
  free: "#E5E7EB"      // серый
}

// Названия категорий на русском
const CATEGORY_NAMES: Record<keyof StorageStats['by_category_mb'], string> = {
  audio: "Аудио",
  video: "Видео",
  images: "Изображения",
  documents: "Документы",
  other: "Другое"
}

// Компонент круговой диаграммы
function PieChart({
  data,
  size = 200,
  showRemaining = false,
  limitMb = 0
}: {
  data: Array<{ label: string; value: number; color: string }>
  size?: number
  showRemaining?: boolean
  limitMb?: number
}) {
  const radius = size / 2
  const strokeWidth = 32
  const innerRadius = radius - strokeWidth / 2
  const circumference = 2 * Math.PI * innerRadius

  const [animated, setAnimated] = useState(false)
  const [hovered, setHovered] = useState<{
    label: string
    percentage: number
    value: number
    x: number
    y: number
  } | null>(null)

  let total = 0
  data.forEach(item => {
    total += Math.max(0, item.value)
  })

  // Для диаграммы с оставшимся местом
  const remainingValue = showRemaining && limitMb > 0 ? limitMb - total : 0
  const displayValue = showRemaining ? remainingValue : total

  let offset = 0

  const segments = data.map(item => {
    const value = Math.max(0, item.value)
    const percentage = total > 0 ? value / total : 0
    const length = circumference * percentage

    const segment = {
      ...item,
      percentage,
      length,
      offset
    }

    offset += length
    return segment
  })

  useEffect(() => {
    const id = requestAnimationFrame(() => setAnimated(true))
    return () => cancelAnimationFrame(id)
  }, [])

  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      {/* Tooltip */}
      {hovered && (
        <div
          style={{
            position: 'absolute',
            left: hovered.x,
            top: hovered.y,
            transform: 'translate(-50%, -120%)',
            backgroundColor: '#111827',
            color: 'white',
            padding: '8px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
            zIndex: 10,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            lineHeight: '1.4'
          }}
        >
          <strong>{hovered.label}</strong><br />
          {hovered.value.toFixed(1)} MB ({hovered.percentage.toFixed(1)}%)
        </div>
      )}

      {/* Текст максимального объема сверху */}
      {showRemaining && limitMb > 0 && (
        <div style={{
          position: 'absolute',
          top: '-35px', // Поднимаем выше диаграммы
          left: 0,
          right: 0,
          textAlign: 'center',
          fontSize: '13px',
          color: '#6B7280',
          fontWeight: '500'
        }}>
          Максимум: {limitMb} MB
        </div>
      )}

      <svg width={size} height={size}>
        {/* Фон */}
        <circle
          cx={radius}
          cy={radius}
          r={innerRadius}
          fill="none"
          stroke="#F3F4F6"
          strokeWidth={strokeWidth}
        />

        {segments.map((segment, index) => {
          if (segment.percentage <= 0) return null

          const midAngle =
            (segment.offset + segment.length / 2) / circumference * 360 - 90
          const midRad = (midAngle * Math.PI) / 180

          const tooltipX = radius + innerRadius * Math.cos(midRad)
          const tooltipY = radius + innerRadius * Math.sin(midRad)

          return (
            <circle
              key={index}
              cx={radius}
              cy={radius}
              r={innerRadius}
              fill="none"
              stroke={segment.color}
              strokeWidth={hovered?.label === segment.label ? strokeWidth + 6 : strokeWidth}
              strokeDasharray={
                animated
                  ? `${segment.length} ${circumference - segment.length}`
                  : `0 ${circumference}`
              }
              strokeDashoffset={-segment.offset}
              style={{
                transition: 'stroke-dasharray 1s ease, stroke-width 0.2s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={() =>
                setHovered({
                  label: segment.label,
                  percentage: segment.percentage * 100,
                  value: segment.value,
                  x: tooltipX,
                  y: tooltipY
                })
              }
              onMouseLeave={() => setHovered(null)}
            />
          )
        })}

        {/* Центр */}
        <text
          x={radius}
          y={radius - 8}
          textAnchor="middle"
          fontSize="16"
          fontWeight="700"
          fill="#111827"
        >
          {displayValue > 0 ? displayValue.toFixed(1) : '0'} MB
        </text>
        <text
          x={radius}
          y={radius + 12}
          textAnchor="middle"
          fontSize="12"
          fill="#6B7280"
          fontWeight="500"
        >
          {showRemaining ? 'осталось' : 'всего'}
        </text>
      </svg>
    </div>
  )
}

// Компонент легенды с ховером
function LegendItem({
  label,
  color,
  value,
  percentage
}: {
  label: string
  color: string
  value: number
  percentage: number
}) {
  const [showTooltip, setShowTooltip] = useState(false)
  const legendRef = useRef<HTMLDivElement>(null)

  return (
    <div
      ref={legendRef}
      style={styles.legendItem}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Квадрат цвета */}
      <div style={{
        ...styles.legendColor,
        backgroundColor: color,
        width: '18px',
        height: '18px',
        borderRadius: '4px'
      }} />

      {/* Название */}
      <span style={styles.legendLabel}>{label}</span>

      {/* Всплывающая подсказка */}
      {showTooltip && (
        <div style={{
          ...styles.legendTooltip,
          left: legendRef.current ? legendRef.current.offsetWidth + 12 : '100%',
          transform: 'translateY(-50%)'
        }}>
          <strong>{label}</strong><br />
          {value.toFixed(1)} MB ({percentage.toFixed(1)}%)
        </div>
      )}
    </div>
  )
}

interface StorageStatsProps {
  onFileUploaded?: () => void
}

export default function StorageStats({ onFileUploaded }: StorageStatsProps) {
  const [stats, setStats] = useState<StorageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    try {
      setLoading(true)
      const data = await getStorageStats()
      console.log("Получена статистика:", data) // Для отладки
      setStats(data)
      setError(null)
    } catch (err) {
      console.error("Ошибка при загрузке статистики:", err)
      setError("Не удалось загрузить статистику")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  // Если пришел onFileUploaded, обновляем статистику
  useEffect(() => {
    if (onFileUploaded) {
      const timeoutId = setTimeout(() => {
        fetchStats()
      }, 500) // Небольшая задержка, чтобы сервер успел обработать файл

      return () => clearTimeout(timeoutId)
    }
  }, [onFileUploaded])

  if (loading) {
    return (
      <div style={styles.container}>
        <h2 style={styles.title}>Статистика хранилища</h2>
        <div style={styles.loading}>
          <div style={styles.spinner} />
          <span>Загрузка статистики...</span>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div style={styles.container}>
        <h2 style={styles.title}>Статистика хранилища</h2>
        <div style={styles.error}>
          <div style={styles.errorIcon}>⚠️</div>
          <span>{error}</span>
          <button
            onClick={fetchStats}
            style={styles.retryButton}
          >
            Повторить
          </button>
        </div>
      </div>
    )
  }

  // Расчет процентов
  const usedPercentage = (stats.total_used_mb / stats.limit_mb) * 100
  const freePercentage = (stats.free_mb / stats.limit_mb) * 100

  // Данные для диаграммы использования места (показываем занятое место как сегмент)
  const storageData = [
    {
      label: "Занято",
      value: stats.total_used_mb,
      color: STORAGE_COLORS.used
    }
  ].filter(item => item.value > 0)

  // Данные для диаграммы по категориям
  const categoryData = Object.entries(stats.by_category_mb)
    .map(([key, value]) => ({
      label: CATEGORY_NAMES[key as keyof typeof stats.by_category_mb],
      value: value,
      color: CATEGORY_COLORS[key as keyof typeof CATEGORY_COLORS]
    }))
    .filter(item => item.value > 0) // Показываем только ненулевые категории

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Статистика хранилища</h2>

      <div style={styles.statsGrid}>
        {/* Первая диаграмма: Оставшееся место */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Оставшееся место</h3>
          <div style={styles.chartContainer}>
            <div style={{ position: 'relative' }}>
              <PieChart
                data={storageData}
                size={200}
                showRemaining={true}
                limitMb={stats.limit_mb}
              />
            </div>
          </div>

          <div style={styles.legendContainer}>
            <LegendItem
              label="Занято"
              color={STORAGE_COLORS.used}
              value={stats.total_used_mb}
              percentage={usedPercentage}
            />
            <LegendItem
              label="Свободно"
              color={STORAGE_COLORS.free}
              value={stats.free_mb}
              percentage={freePercentage}
            />
          </div>
        </div>

        {/* Вторая диаграмма: Распределение по категориям */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Распределение по типам файлов</h3>
          <div style={styles.chartContainer}>
            <PieChart
              data={categoryData}
              size={200}
            />
          </div>

          <div style={styles.legendContainer}>
            {categoryData.map((item, index) => {
              const totalCategories = Object.values(stats.by_category_mb).reduce((a, b) => a + b, 0)
              const percentage = totalCategories > 0 ? (item.value / totalCategories) * 100 : 0

              return (
                <LegendItem
                  key={index}
                  label={item.label}
                  color={item.color}
                  value={item.value}
                  percentage={percentage}
                />
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb',
    flexShrink: 0,
  },
  title: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#111827',
    margin: '0 0 20px 0',
    paddingBottom: '12px',
    borderBottom: '1px solid #E5E7EB'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    color: '#6B7280',
    fontSize: '14px',
    gap: '12px'
  },
  spinner: {
    width: '32px',
    height: '32px',
    border: '3px solid #f3f4f6',
    borderTopColor: '#3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  error: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    color: '#dc2626',
    fontSize: '14px',
    gap: '12px',
    textAlign: 'center'
  },
  errorIcon: {
    fontSize: '24px'
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    marginTop: '8px'
  },
  statsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  chartCard: {
    backgroundColor: '#f9fafb',
    borderRadius: '10px',
    padding: '20px',
    position: 'relative',
  },
  chartTitle: {
    fontSize: '15px',
    fontWeight: '600',
    color: '#374151',
    margin: '0 0 20px 0',
    textAlign: 'center'
  },
  chartContainer: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '24px',
    minHeight: '250px' // Добавляем место для текста сверху
  },
  legendContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    position: 'relative',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    position: 'relative',
    padding: '8px 12px',
    borderRadius: '6px',
    backgroundColor: 'white',
    transition: 'background-color 0.2s ease',
  },
  legendColor: {
    flexShrink: 0
  },
  legendLabel: {
    color: '#374151',
    fontSize: '14px',
    fontWeight: '500'
  },
  legendTooltip: {
    position: 'absolute',
    top: '50%',
    backgroundColor: '#111827',
    color: 'white',
    padding: '8px 12px',
    borderRadius: '6px',
    fontSize: '12px',
    whiteSpace: 'nowrap',
    zIndex: 10,
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    lineHeight: '1.4',
    pointerEvents: 'none',
  }
}

// Добавляем стили для анимации спиннера
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement("style")
  styleSheet.textContent = `
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `
  document.head.appendChild(styleSheet)
}