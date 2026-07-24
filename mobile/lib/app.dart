import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/behavioral_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/auth/forgot_password_screen.dart';
import 'screens/auth/otp_verification_screen.dart';
import 'screens/auth/mfa_setup_screen.dart';
import 'screens/home/dashboard_screen.dart';
import 'screens/home/accounts_screen.dart';
import 'screens/home/transfers_screen.dart';
import 'screens/home/payments_screen.dart';
import 'screens/home/cards_screen.dart';
import 'screens/home/loans_screen.dart';
import 'screens/home/profile_screen.dart';
import 'screens/details/transaction_detail_screen.dart';
import 'screens/details/account_detail_screen.dart';
import 'screens/details/card_detail_screen.dart';
import 'screens/details/loan_detail_screen.dart';
import 'screens/details/beneficiary_screen.dart';
import 'screens/details/emi_calculator_screen.dart';

class BehavioralBiometricBankingApp extends StatelessWidget {
  const BehavioralBiometricBankingApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();

    return MaterialApp(
      title: 'SecureBank',
      debugShowCheckedModeBanner: false,
      theme: themeProvider.themeData,
      initialRoute: '/splash',
      onGenerateRoute: (settings) {
        switch (settings.name) {
          case '/splash':
            return MaterialPageRoute(
              builder: (_) => const SplashScreen(),
            );
          case '/login':
            return MaterialPageRoute(
              builder: (_) => const LoginScreen(),
            );
          case '/register':
            return MaterialPageRoute(
              builder: (_) => const RegisterScreen(),
            );
          case '/forgot-password':
            return MaterialPageRoute(
              builder: (_) => const ForgotPasswordScreen(),
            );
          case '/otp-verification':
            final args = settings.arguments as Map<String, dynamic>? ?? {};
            return MaterialPageRoute(
              builder: (_) => OtpVerificationScreen(
                email: args['email'] ?? '',
                purpose: args['purpose'] ?? 'verification',
              ),
            );
          case '/mfa-setup':
            return MaterialPageRoute(
              builder: (_) => const MfaSetupScreen(),
            );
          case '/dashboard':
            return MaterialPageRoute(
              builder: (_) => const MainNavigationShell(),
            );
          case '/transaction-detail':
            final transactionId = settings.arguments as String? ?? '';
            return MaterialPageRoute(
              builder: (_) => TransactionDetailScreen(
                transactionId: transactionId,
              ),
            );
          case '/account-detail':
            final accountId = settings.arguments as String? ?? '';
            return MaterialPageRoute(
              builder: (_) => AccountDetailScreen(accountId: accountId),
            );
          case '/card-detail':
            final cardId = settings.arguments as String? ?? '';
            return MaterialPageRoute(
              builder: (_) => CardDetailScreen(cardId: cardId),
            );
          case '/loan-detail':
            final loanId = settings.arguments as String? ?? '';
            return MaterialPageRoute(
              builder: (_) => LoanDetailScreen(loanId: loanId),
            );
          case '/beneficiaries':
            return MaterialPageRoute(
              builder: (_) => const BeneficiaryScreen(),
            );
          case '/emi-calculator':
            return MaterialPageRoute(
              builder: (_) => const EmiCalculatorScreen(),
            );
          case '/transfers':
            return MaterialPageRoute(
              builder: (_) => const TransfersScreen(),
            );
          case '/accounts':
            return MaterialPageRoute(
              builder: (_) => const AccountsScreen(),
            );
          case '/cards':
            return MaterialPageRoute(
              builder: (_) => const CardsScreen(),
            );
          case '/loans':
            return MaterialPageRoute(
              builder: (_) => const LoansScreen(),
            );
          case '/payments':
            return MaterialPageRoute(
              builder: (_) => const PaymentsScreen(),
            );
          default:
            return MaterialPageRoute(
              builder: (_) => const SplashScreen(),
            );
        }
      },
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    final authProvider = context.read<AuthProvider>();
    await authProvider.init();

    if (!mounted) return;

    if (authProvider.isAuthenticated) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF1A237E),
              Color(0xFF283593),
              Color(0xFF3949AB),
            ],
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                borderRadius: BorderRadius.circular(30),
              ),
              child: const Icon(
                Icons.security,
                size: 60,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'SecureBank',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'AI-Powered Behavioral Banking',
              style: TextStyle(
                fontSize: 16,
                color: Colors.white.withOpacity(0.8),
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DashboardScreen(),
    AccountsScreen(),
    TransfersScreen(),
    ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BehavioralProvider>().handleNavigation('dashboard');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() => _currentIndex = index);
          final screens = [
            'dashboard',
            'accounts',
            'transfers',
            'profile'
          ];
          context.read<BehavioralProvider>().handleNavigation(screens[index]);
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_balance),
            label: 'Accounts',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.send_money),
            label: 'Transfer',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
