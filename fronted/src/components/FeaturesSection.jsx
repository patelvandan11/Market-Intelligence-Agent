import {
  FaBrain,
  FaChartLine,
  FaUserSecret,
  FaChartBar,
  FaGlobe,
  FaShieldAlt,
} from 'react-icons/fa';

const features = [
  {
    title: 'AI-Powered Analysis',
    description: 'Machine learning algorithms analyze market behavior and predict upcoming patterns.',
    icon: <FaBrain className="text-pink-500 text-4xl" />,
  },
  {
    title: 'Real-time Monitoring',
    description: 'Live insights from markets, news feeds, and economic indicators.',
    icon: <FaChartLine className="text-cyan-400 text-4xl" />,
  },
  {
    title: 'Competitor Tracking',
    description: 'Get strategic intelligence about your competitors in real time.',
    icon: <FaUserSecret className="text-green-400 text-4xl" />,
  },
  {
    title: 'Custom Dashboards',
    description: 'Tailor KPIs and trends to your exact business needs.',
    icon: <FaChartBar className="text-orange-500 text-4xl" />,
  },
  {
    title: 'Global Data Coverage',
    description: 'World-wide access to financial, stock, commodity, and currency data.',
    icon: <FaGlobe className="text-purple-400 text-4xl" />,
  },
  {
    title: 'Risk Detection',
    description: 'Predictive models identify opportunities and threats early.',
    icon: <FaShieldAlt className="text-yellow-400 text-4xl" />,
  },
];

const FeaturesSection = () => {
  return (
    <section className="bg-gradient-to-b from-[#1e293b] to-[#0f172a] py-16 text-white">
      <div className="text-center mb-14">
        <h2 className="text-4xl font-bold mb-4">
          Powerful Features for <span className="text-cyan-400">Market Leaders</span>
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Everything you need to outpace your competition — real-time insights, automation, and global data intelligence.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-8 max-w-6xl mx-auto px-6">
        {features.map((feature, i) => (
          <div
            key={i}
            className="bg-[#1f2a3e] hover:bg-[#24344d] rounded-2xl p-6 shadow-xl transition"
          >
            <div className="mb-4">{feature.icon}</div>
            <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-gray-400 text-sm">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;
