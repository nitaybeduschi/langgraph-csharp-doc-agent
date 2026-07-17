using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace SampleProject.Services
{
    /// <summary>
    /// Service responsible for managing customer operations.
    /// </summary>
    public class CustomerService
    {
        private readonly ICustomerRepository _repository;
        private readonly ILogger<CustomerService> _logger;

        public CustomerService(
            ICustomerRepository repository,
            ILogger<CustomerService> logger)
        {
            _repository = repository;
            _logger = logger;
        }

        /// <summary>
        /// Retrieves a customer by its identifier.
        /// </summary>
        /// <param name="customerId">Customer identifier.</param>
        /// <returns>The customer if found; otherwise null.</returns>
        public async Task<Customer?> GetByIdAsync(Guid customerId)
        {
            _logger.LogInformation("Searching customer {CustomerId}", customerId);

            return await _repository.GetByIdAsync(customerId);
        }

        /// <summary>
        /// Creates a new customer.
        /// </summary>
        /// <param name="customer">Customer data.</param>
        /// <exception cref="ArgumentNullException"></exception>
        /// <exception cref="InvalidOperationException"></exception>
        public async Task CreateAsync(Customer customer)
        {
            if (customer == null)
                throw new ArgumentNullException(nameof(customer));

            var exists = await _repository.ExistsAsync(customer.Email);

            if (exists)
                throw new InvalidOperationException("Customer already exists.");

            customer.CreatedAt = DateTime.UtcNow;

            await _repository.AddAsync(customer);

            _logger.LogInformation(
                "Customer {CustomerId} created successfully.",
                customer.Id);
        }

        /// <summary>
        /// Updates the customer's email address.
        /// </summary>
        /// <param name="customerId">Customer identifier.</param>
        /// <param name="newEmail">New email address.</param>
        /// <returns>True if updated successfully.</returns>
        public async Task<bool> UpdateEmailAsync(Guid customerId, string newEmail)
        {
            var customer = await _repository.GetByIdAsync(customerId);

            if (customer == null)
                return false;

            customer.Email = newEmail;

            await _repository.UpdateAsync(customer);

            return true;
        }

        /// <summary>
        /// Returns all active customers ordered by name.
        /// </summary>
        public async Task<IReadOnlyCollection<Customer>> GetActiveCustomersAsync()
        {
            var customers = await _repository.GetAllAsync();

            return customers
                .Where(c => c.IsActive)
                .OrderBy(c => c.Name)
                .ToList();
        }

        /// <summary>
        /// Deactivates a customer.
        /// </summary>
        /// <param name="customerId">Customer identifier.</param>
        public async Task DeactivateAsync(Guid customerId)
        {
            var customer = await _repository.GetByIdAsync(customerId);

            if (customer == null)
                throw new KeyNotFoundException("Customer not found.");

            customer.IsActive = false;

            await _repository.UpdateAsync(customer);

            _logger.LogInformation(
                "Customer {CustomerId} deactivated.",
                customerId);
        }
    }
}