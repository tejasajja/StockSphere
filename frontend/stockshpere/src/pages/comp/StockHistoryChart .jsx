
import { Line } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

// eslint-disable-next-line react/prop-types
const StockHistoryChart = ({ stockHistory }) => {
    // const [jwt] = useLocalState("", "jwt");

    const chartData = {
        // eslint-disable-next-line react/prop-types
        labels: stockHistory.map(item => item.date),
        datasets: [
            {
                label: 'Open',
                // eslint-disable-next-line react/prop-types
                data: stockHistory.map(item => item.Open),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
            {
                label: 'Close',
                // eslint-disable-next-line react/prop-types
                data: stockHistory.map(item => item.Close),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            },
            {
                label: 'High',
                // eslint-disable-next-line react/prop-types
                data: stockHistory.map(item => item.High),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
            {
                label: 'Low',
                // eslint-disable-next-line react/prop-types
                data: stockHistory.map(item => item.Low),
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
            }
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Stock History',
            },
        },
    };

    return (
        <Card className="justify-center m-16 mt-12 h-[390px] w-[600px] dark:text-white">
            <CardHeader>
                <CardTitle className="text-3xl font-bold font-mono md:text-left transition-colors hover:text-primary">
                    Stock Trends
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-full w-full">
                    <Line data={chartData} options={options} />
                </div>
            </CardContent>
        </Card>
    );
};

export default StockHistoryChart;
