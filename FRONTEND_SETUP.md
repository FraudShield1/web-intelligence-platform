# Frontend Setup Guide
## React Dashboard for Web Intelligence Platform

---

## 1. PROJECT STRUCTURE

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── index.tsx
│   ├── App.tsx
│   ├── App.css
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Layout.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Sites.tsx
│   │   │   ├── SiteDetail.tsx
│   │   │   ├── Jobs.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── Login.tsx
│   │   │
│   │   ├── sites/
│   │   │   ├── SiteCard.tsx
│   │   │   ├── SiteForm.tsx
│   │   │   ├── SiteFilter.tsx
│   │   │   └── SiteTable.tsx
│   │   │
│   │   ├── jobs/
│   │   │   ├── JobStatus.tsx
│   │   │   ├── JobList.tsx
│   │   │   └── JobDetail.tsx
│   │   │
│   │   ├── analytics/
│   │   │   ├── DashboardMetrics.tsx
│   │   │   ├── Charts.tsx
│   │   │   ├── MethodPerformance.tsx
│   │   │   ├── SelectorReliability.tsx
│   │   │   └── Alerts.tsx
│   │   │
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Modal.tsx
│   │       ├── Loading.tsx
│   │       ├── Toast.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useAuth.ts
│   │   ├── useSites.ts
│   │   ├── useJobs.ts
│   │   └── useAnalytics.ts
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── sites.ts
│   │   ├── jobs.ts
│   │   ├── blueprints.ts
│   │   └── analytics.ts
│   │
│   ├── store/
│   │   ├── index.ts
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── sitesSlice.ts
│   │   │   ├── jobsSlice.ts
│   │   │   └── analyticsSlice.ts
│   │   └── middleware/
│   │
│   ├── types/
│   │   ├── index.ts
│   │   ├── site.ts
│   │   ├── job.ts
│   │   ├── blueprint.ts
│   │   └── analytics.ts
│   │
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── helpers.ts
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── components.css
│   │
│   └── config/
│       └── config.ts
│
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── Dockerfile
└── .env.example
```

---

## 2. PACKAGE.JSON

```json
{
  "name": "web-intelligence-platform-frontend",
  "version": "1.0.0",
  "description": "Web Intelligence Platform Dashboard",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "@reduxjs/toolkit": "^1.9.7",
    "react-redux": "^8.1.3",
    "recharts": "^2.10.3",
    "date-fns": "^2.30.0",
    "lucide-react": "^0.294.0",
    "tailwindcss": "^3.4.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@types/node": "^20.10.4",
    "react-scripts": "5.0.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

---

## 3. KEY COMPONENTS

### 3.1 Dashboard Component

```tsx
// src/components/pages/Dashboard.tsx
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { BarChart, PieChart, LineChart } from 'recharts';
import DashboardMetrics from '../analytics/DashboardMetrics';
import Alerts from '../analytics/Alerts';

export const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const { metrics, loading, error } = useSelector(state => state.analytics);

  useEffect(() => {
    // Fetch dashboard data on mount
    dispatch(fetchDashboardMetrics());
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard 
          title="Total Sites" 
          value={metrics.total_sites}
          trend="+12% this week"
        />
        <MetricCard 
          title="Discovery Success" 
          value={`${(metrics.success_rate * 100).toFixed(1)}%`}
          trend="improving"
        />
        <MetricCard 
          title="Avg Discovery Time" 
          value={`${metrics.avg_discovery_time}s`}
          trend="-8.5% faster"
        />
        <MetricCard 
          title="Cost per Item" 
          value={`$${metrics.cost_per_item.toFixed(3)}`}
          trend="-5% optimized"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <ChartCard title="Sites by Platform">
          <PieChart data={metrics.platform_distribution} />
        </ChartCard>
        <ChartCard title="Discovery Success Trend">
          <LineChart data={metrics.success_trend} />
        </ChartCard>
      </div>

      {/* Alerts & Issues */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Alerts & Issues</h2>
        <Alerts alerts={metrics.alerts} />
      </div>
    </div>
  );
};
```

### 3.2 Sites Management Component

```tsx
// src/components/pages/Sites.tsx
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import SiteTable from '../sites/SiteTable';
import SiteFilter from '../sites/SiteFilter';
import SiteForm from '../sites/SiteForm';
import { fetchSites, createSite } from '../../store/slices/sitesSlice';

export const Sites: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    platform: '',
    search: ''
  });

  const dispatch = useDispatch();
  const { sites, loading, error, total } = useSelector(state => state.sites);

  useEffect(() => {
    dispatch(fetchSites(filters));
  }, [filters, dispatch]);

  const handleAddSite = async (domain: string) => {
    await dispatch(createSite({ domain }));
    setShowForm(false);
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Sites</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add New Site
        </button>
      </div>

      <SiteFilter onFilterChange={setFilters} />
      
      {showForm && (
        <SiteForm 
          onSubmit={handleAddSite}
          onCancel={() => setShowForm(false)}
        />
      )}

      <SiteTable 
        sites={sites}
        loading={loading}
        error={error}
        total={total}
      />
    </div>
  );
};
```

### 3.3 Jobs Status Component

```tsx
// src/components/pages/Jobs.tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import JobList from '../jobs/JobList';
import { fetchJobs } from '../../store/slices/jobsSlice';

export const Jobs: React.FC = () => {
  const dispatch = useDispatch();
  const { jobs, loading } = useSelector(state => state.jobs);

  useEffect(() => {
    // Poll for job updates every 5 seconds
    dispatch(fetchJobs());
    const interval = setInterval(() => {
      dispatch(fetchJobs());
    }, 5000);

    return () => clearInterval(interval);
  }, [dispatch]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Active Jobs</h1>
      <JobList jobs={jobs} loading={loading} />
    </div>
  );
};
```

### 3.4 Analytics Component

```tsx
// src/components/pages/Analytics.tsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MethodPerformance from '../analytics/MethodPerformance';
import SelectorReliability from '../analytics/SelectorReliability';
import { fetchAnalytics } from '../../store/slices/analyticsSlice';

export const Analytics: React.FC = () => {
  const dispatch = useDispatch();
  const { analytics, loading } = useSelector(state => state.analytics);

  useEffect(() => {
    dispatch(fetchAnalytics());
  }, [dispatch]);

  if (loading) return <div>Loading analytics...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Analytics</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Method Performance</h2>
          <MethodPerformance data={analytics.method_performance} />
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Selector Reliability</h2>
          <SelectorReliability data={analytics.selector_reliability} />
        </div>
      </div>
    </div>
  );
};
```

---

## 4. HOOKS

### 4.1 useApi Hook

```tsx
// src/hooks/useApi.ts
import { useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = <T,>(url: string): UseApiState<T> => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(url, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setState({
          data: response.data,
          loading: false,
          error: null
        });
      } catch (err) {
        const error = err as AxiosError;
        setState({
          data: null,
          loading: false,
          error: error.message
        });
      }
    };

    fetchData();
  }, [url]);

  return state;
};
```

### 4.2 useSites Hook

```tsx
// src/hooks/useSites.ts
import { useDispatch, useSelector } from 'react-redux';
import { useCallback } from 'react';
import { fetchSites, createSite } from '../store/slices/sitesSlice';

export const useSites = () => {
  const dispatch = useDispatch();
  const { sites, loading, error, total } = useSelector(state => state.sites);

  const getSites = useCallback((filters) => {
    dispatch(fetchSites(filters));
  }, [dispatch]);

  const addSite = useCallback((domain: string) => {
    dispatch(createSite({ domain }));
  }, [dispatch]);

  return {
    sites,
    loading,
    error,
    total,
    getSites,
    addSite
  };
};
```

---

## 5. REDUX STORE

### 5.1 Sites Slice

```tsx
// src/store/slices/sitesSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as sitesService from '../../services/sites';

export const fetchSites = createAsyncThunk(
  'sites/fetchSites',
  async (filters) => {
    return await sitesService.getSites(filters);
  }
);

export const createSite = createAsyncThunk(
  'sites/createSite',
  async (data) => {
    return await sitesService.createSite(data);
  }
);

const sitesSlice = createSlice({
  name: 'sites',
  initialState: {
    sites: [],
    loading: false,
    error: null,
    total: 0
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSites.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchSites.fulfilled, (state, action) => {
        state.sites = action.payload.sites;
        state.total = action.payload.total;
        state.loading = false;
      })
      .addCase(fetchSites.rejected, (state, action) => {
        state.error = action.error.message;
        state.loading = false;
      })
      .addCase(createSite.fulfilled, (state, action) => {
        state.sites.unshift(action.payload);
      });
  }
});

export default sitesSlice.reducer;
```

---

## 6. SERVICES

### 6.1 Sites Service

```tsx
// src/services/sites.ts
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add JWT token to requests
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getSites = async (filters) => {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.platform) params.append('platform', filters.platform);
  if (filters.search) params.append('search', filters.search);
  
  const response = await axiosInstance.get('/sites', { params });
  return response.data;
};

export const getSiteById = async (siteId: string) => {
  const response = await axiosInstance.get(`/sites/${siteId}`);
  return response.data;
};

export const createSite = async (data: { domain: string }) => {
  const response = await axiosInstance.post('/sites', data);
  return response.data;
};

export const updateSite = async (siteId: string, data) => {
  const response = await axiosInstance.put(`/sites/${siteId}`, data);
  return response.data;
};

export const deleteSite = async (siteId: string) => {
  await axiosInstance.delete(`/sites/${siteId}`);
};
```

---

## 7. TAILWIND CONFIGURATION

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#1F2937',
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444'
      }
    }
  },
  plugins: []
}
```

---

## 8. DOCKERFILE

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Serve
RUN npm install -g serve
EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
```

---

## 9. ENVIRONMENT TEMPLATE

```
# .env.example
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

---

## 10. GETTING STARTED

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm build

# Run Docker
docker build -t wip-frontend .
docker run -p 3000:3000 wip-frontend
```

---

## 11. KEY FEATURES

### Real-time Updates
- WebSocket connection for job status updates
- Auto-refresh analytics every 30 seconds
- Poll job queue every 5 seconds

### User Authentication
- JWT token stored in localStorage
- Protected routes
- Automatic token refresh

### Responsive Design
- Mobile-first approach
- Tailwind CSS utilities
- Responsive grid layouts

### Error Handling
- Global error boundary
- Toast notifications
- Retry mechanisms

### Performance
- Code splitting with React Router
- Lazy loading of components
- Memoization of expensive computations

---

## 12. DEPLOYMENT

### Development
```bash
npm start
```

### Production
```bash
npm run build
docker build -t wip-frontend .
docker run -d -p 3000:3000 wip-frontend
```

### With Docker Compose
```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:3000"
  environment:
    - REACT_APP_API_URL=http://api:8000/api/v1
  depends_on:
    - api
```


