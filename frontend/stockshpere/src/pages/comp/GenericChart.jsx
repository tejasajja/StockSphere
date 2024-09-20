import  { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useLocalState } from '@/utils/usingLocalStorage';
import PropTypes from 'prop-types';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
  } from 'chart.js';
  
  ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
  );
const GenericChart = ({ url, chartOptions, title }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [],
  });
  const [jwt] = useLocalState("", "jwt");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${jwt}`,
          },
        });
        if (response.ok) {
          const fetchedData = await response.json();
          setChartData(chartOptions.transformData(fetchedData));
        } else {
          console.error('HTTP error:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [jwt, url, chartOptions.transformData]); // React to changes in jwt, url, or the transform function

  return (
    <Card className="justify-center m-16 mt-28 h-[490px] w-[600px] dark:text-white">
      <CardHeader>
        <CardTitle className="text-3xl font-bold font-mono md:text-left transition-colors hover:text-primary">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-full w-full">
          <Bar data={chartData} options={chartOptions.options} />
        </div>
      </CardContent>
    </Card>
  );
};

GenericChart.propTypes = {
  url: PropTypes.string.isRequired,
  chartOptions: PropTypes.shape({
    transformData: PropTypes.func.isRequired,
    options: PropTypes.object.isRequired,
  }).isRequired,
  title: PropTypes.string.isRequired,
};

export default GenericChart;
